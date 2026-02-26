import type { VercelRequest, VercelResponse } from '@vercel/node'

const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'

interface ReferenceCharacter {
  name: string
  description?: string
  tags?: string[]
}

interface GeneratedSample {
  title: string
  description: string
  name: string
  profile: string
  backgroundIntro: string
  worldPrompt: string
  firstDaySituation: string
  openingMessage: string
  genre: string
  hashtags: string[]
}

function createPrompt(tags: string[], referenceCharacters: ReferenceCharacter[], count: number): string {
  // 참고 캐릭터 정보 요약
  let refInfo = ''
  referenceCharacters.slice(0, 3).forEach((char, i) => {
    refInfo += `\n${i + 1}. ${char.name || ''}`
    if (char.description) {
      refInfo += `\n   설명: ${char.description.slice(0, 200)}...`
    }
    if (char.tags) {
      refInfo += `\n   태그: ${char.tags.slice(0, 5).join(', ')}`
    }
  })

  return `당신은 AI 캐릭터 챗봇 전문 크리에이터입니다.
현재 인기 있는 캐릭터들을 분석하여 새로운 캐릭터 제작 가이드를 만들어주세요.

## 주어진 태그 조합
${tags.join(', ')}

## 참고할 인기 캐릭터
${refInfo}

## 요청사항
위 태그 조합을 기반으로 ${count}개의 독창적인 캐릭터 제작 가이드를 생성해주세요.
각 캐릭터마다 다음 정보를 포함해야 합니다:

1. **작품 제목 (title)**: 이 캐릭터 작품의 매력적인 제목 (예: "달빛 아래의 기사", "금지된 계약")
2. **작품 소개글 (description)**: 작품 전체를 소개하는 매력적인 문구 (100자 이상)
3. **캐릭터명 (name)**: 태그와 어울리는 매력적인 이름
4. **캐릭터 프로필 (profile)**: 외모, 성격, 말투를 포함한 상세 프로필 (200자 이상)
5. **배경 소개글 (backgroundIntro)**: 세계관 배경 간단 소개 (50자 이상)
6. **세계관 프롬프트 (worldPrompt)**: AI에게 전달할 세계관 시스템 프롬프트 (150자 이상, 구체적인 설정 포함)
7. **첫날 상황 (firstDaySituation)**: 유저와 캐릭터가 처음 만나는 상황 설명 (100자 이상)
8. **시작 메시지 (openingMessage)**: 캐릭터가 유저에게 보내는 첫 대사 (캐릭터의 말투와 성격이 드러나도록)
9. **대표 장르 (genre)**: 로맨스, 판타지, 드라마, 무협, 공포, 스포츠, 기타 중 택1
10. **해시태그 (hashtags)**: 검색용 해시태그 5개 (배열 형태)

## 응답 형식 (JSON)
\`\`\`json
[
  {
    "title": "작품 제목",
    "description": "작품 소개글",
    "name": "캐릭터 이름",
    "profile": "외모, 성격, 말투를 포함한 상세 프로필",
    "backgroundIntro": "세계관 배경 소개",
    "worldPrompt": "AI 시스템 프롬프트용 세계관 설정",
    "firstDaySituation": "첫 만남 상황 설명",
    "openingMessage": "캐릭터의 첫 대사",
    "genre": "로맨스",
    "hashtags": ["태그1", "태그2", "태그3", "태그4", "태그5"]
  }
]
\`\`\`

**중요**: 반드시 JSON 형식으로만 응답하세요. 추가 설명은 필요 없습니다.`
}

function parseGeneratedSamples(text: string, expectedCount: number): GeneratedSample[] {
  try {
    // JSON 추출 (마크다운 코드 블록 제거)
    let cleanText = text.trim()
    if (cleanText.includes('```json')) {
      cleanText = cleanText.split('```json')[1].split('```')[0]
    } else if (cleanText.includes('```')) {
      cleanText = cleanText.split('```')[1].split('```')[0]
    }
    cleanText = cleanText.trim()

    // JSON 파싱
    const samples = JSON.parse(cleanText) as GeneratedSample[]

    if (!Array.isArray(samples)) {
      throw new Error('응답이 리스트 형식이 아닙니다')
    }

    // 필수 필드 확인
    const requiredFields = [
      'title', 'description', 'name', 'profile', 'backgroundIntro',
      'worldPrompt', 'firstDaySituation', 'openingMessage', 'genre', 'hashtags'
    ] as const

    for (const sample of samples) {
      for (const field of requiredFields) {
        if (!(field in sample)) {
          if (field === 'hashtags') {
            (sample as any)[field] = []
          } else {
            (sample as any)[field] = '정보 없음'
          }
        }
      }
    }

    return samples.slice(0, expectedCount)
  } catch {
    // 폴백: 빈 샘플 반환
    return Array.from({ length: expectedCount }, (_, i) => ({
      title: `샘플 ${i + 1}`,
      description: 'Gemini API 응답 파싱에 실패했습니다.',
      name: `캐릭터 ${i + 1}`,
      profile: '생성 실패',
      backgroundIntro: '생성 실패',
      worldPrompt: '생성 실패',
      firstDaySituation: '생성 실패',
      openingMessage: '생성 실패',
      genre: '기타',
      hashtags: []
    }))
  }
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // CORS 설정
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    return res.status(200).end()
  }

  if (req.method !== 'POST') {
    console.log('[generate-character] Method not allowed:', req.method)
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const apiKey = process.env.GEMINI_API_KEY
  console.log('[generate-character] API Key exists:', !!apiKey)

  if (!apiKey) {
    console.error('[generate-character] Gemini API 키가 설정되지 않았습니다.')
    return res.status(500).json({ error: 'Gemini API 키가 설정되지 않았습니다. Vercel 환경 변수를 확인하세요.' })
  }

  try {
    const { tag_combinations } = req.body as {
      tag_combinations: string[][]
    }

    console.log('[generate-character] Received tag_combinations:', tag_combinations)

    if (!tag_combinations || !Array.isArray(tag_combinations)) {
      return res.status(400).json({ error: 'tag_combinations 배열이 필요합니다.' })
    }

    const allSamples: (GeneratedSample & { id: number; tags: string[]; basedOn: string[] })[] = []

    for (let i = 0; i < tag_combinations.length; i++) {
      const tags = tag_combinations[i]
      console.log(`[generate-character] Processing tag combination ${i + 1}:`, tags)

      const prompt = createPrompt(tags, [], 1)

      console.log(`[generate-character] Calling Gemini API for combination ${i + 1}`)
      const geminiResponse = await fetch(`${GEMINI_API_URL}?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{
            parts: [{ text: prompt }]
          }],
          generationConfig: {
            temperature: 0.8,
            topK: 40,
            topP: 0.95,
            maxOutputTokens: 16384,
          }
        })
      })

      if (!geminiResponse.ok) {
        const errorText = await geminiResponse.text()
        console.error('[generate-character] Gemini API 오류:', geminiResponse.status, errorText)
        throw new Error(`Gemini API 오류 (${geminiResponse.status}): ${errorText.slice(0, 200)}`)
      }

      const result = await geminiResponse.json()
      console.log('[generate-character] Gemini API response received')

      const generatedText = result.candidates?.[0]?.content?.parts?.[0]?.text || ''
      if (!generatedText) {
        console.error('[generate-character] Empty response from Gemini')
        throw new Error('Gemini API에서 빈 응답을 받았습니다.')
      }

      const samples = parseGeneratedSamples(generatedText, 1)
      console.log(`[generate-character] Parsed ${samples.length} samples`)

      for (const sample of samples) {
        allSamples.push({
          ...sample,
          id: i + 1,
          tags,
          basedOn: []
        })
      }
    }

    console.log('[generate-character] Success! Returning', allSamples.length, 'samples')
    return res.status(200).json({ samples: allSamples })
  } catch (error) {
    console.error('[generate-character] Error:', error)
    const errorMessage = error instanceof Error ? error.message : '캐릭터 샘플 생성에 실패했습니다.'
    return res.status(500).json({ error: errorMessage })
  }
}

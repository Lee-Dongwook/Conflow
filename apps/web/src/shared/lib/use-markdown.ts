import { useEffect, useState } from 'react'

export const useMarkdown = (url: string) => {
  const [content, setContent] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    setIsLoading(true)
    fetch(url)
      .then((res) => res.text())
      .then((text) => {
        setContent(text)
        setIsLoading(false)
      })
      .catch(() => {
        setContent('문서를 불러올 수 없습니다.')
        setIsLoading(false)
      })
  }, [url])

  return { content, isLoading }
}

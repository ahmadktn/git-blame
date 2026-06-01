const API_BASE = 'https://gitblame-backend.cosmologictech.com.ng'

export function useApi() {
  async function startAnalysis(repoUrl: string, maxCommits = 100) {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_url: repoUrl, max_commits: maxCommits }),
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
  }

  async function getJobStatus(jobId: string) {
    const res = await fetch(`${API_BASE}/analyze/${jobId}`)
    if (!res.ok) throw new Error(await res.text())
    return res.json()
  }

  async function getCommits(jobId: string, skip = 0, limit = 50) {
    const res = await fetch(`${API_BASE}/analyze/${jobId}/commits?skip=${skip}&limit=${limit}`)
    if (!res.ok) throw new Error(await res.text())
    return res.json()
  }

  async function pollUntilComplete(jobId: string, onProgress?: (job: any) => void): Promise<any> {
    while (true) {
      const job = await getJobStatus(jobId)
      onProgress?.(job)
      if (job.status === 'complete' || job.status === 'failed') return job
      await new Promise(r => setTimeout(r, 1500))
    }
  }

  return { startAnalysis, getJobStatus, getCommits, pollUntilComplete }
}

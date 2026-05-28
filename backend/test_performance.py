import asyncio
import time
import httpx

API_URL = "http://localhost:8000"
TEST_REPO = "https://github.com/tiangolo/fastapi"  # A real repo to test
COMMITS_TO_FETCH = 20

async def test_cache_speed():
    print(f"--- Testing Speed & Cache ---")
    async with httpx.AsyncClient() as client:
        # 1. First Request (Cache Miss)
        print("1. First Request (Should fetch and analyze...)")
        start = time.time()
        res = await client.post(f"{API_URL}/analyze", json={"repo_url": TEST_REPO, "max_commits": COMMITS_TO_FETCH})
        job = res.json()
        job_id = job["job_id"]
        
        # Poll until complete
        while True:
            status_res = await client.get(f"{API_URL}/analyze/{job_id}")
            status_data = status_res.json()
            if status_data["status"] == "complete":
                break
            elif status_data["status"] == "failed":
                print("Job failed!")
                return
            await asyncio.sleep(0.5)
            
        first_time = time.time() - start
        print(f"   Done! First analysis took: {first_time:.2f} seconds\n")

        # 2. Second Request (Cache Hit)
        print("2. Second Request (Should hit cache...)")
        start2 = time.time()
        res2 = await client.post(f"{API_URL}/analyze", json={"repo_url": TEST_REPO, "max_commits": COMMITS_TO_FETCH})
        second_time = time.time() - start2
        print(f"   Done! Cached response took: {second_time:.4f} seconds")
        print(f"   Speedup: {first_time / second_time:.0f}x faster\n")

async def test_scalability_concurrent_requests():
    print(f"--- Testing Scalability (10 Concurrent Users) ---")
    async with httpx.AsyncClient() as client:
        start = time.time()
        
        # Simulate 10 users requesting cached data at exactly the same time
        tasks = []
        for _ in range(10):
            tasks.append(client.post(f"{API_URL}/analyze", json={"repo_url": TEST_REPO, "max_commits": COMMITS_TO_FETCH}))
            
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start
        
        print(f"   10 concurrent requests handled in {total_time:.4f} seconds")
        print(f"   All returned 202 Accepted? {all(r.status_code == 202 for r in results)}")

if __name__ == "__main__":
    asyncio.run(test_cache_speed())
    asyncio.run(test_scalability_concurrent_requests())

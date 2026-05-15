from playwright.sync_api import sync_playwright
import json

class EkantipurNewsScraper():
    def __init__(self, headless= False):
        self.headless = headless
        self.url = "https://ekantipur.com/"
        self.results= {
           "entertainment_news": [],
           "cartoon_of_the_day": {}
        }

    def run(self):
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=self.headless, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(
                  user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                  viewport={"width": 1280, "height": 720},
                  ignore_https_errors=True,
                  locale="en-US",
                  timezone_id="Asia/Kathmandu",  
                  extra_http_headers={
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://ekantipur.com/"
                  },
                  device_scale_factor=1.0
)
            page = context.new_page()
            page.set_default_timeout(15000) 

            page.add_locator_handler(
                         page.locator("button[data-bs-dismiss='modal']", has_text="Skip"),
    lambda: (
        page.locator("button[data-bs-dismiss='modal']", has_text="Skip").click(),
        page.wait_for_selector("button[data-bs-dismiss='modal']", state="hidden")
    )
) 
            
            try:
               page.goto(f"{self.url}entertainment", wait_until="networkidle")
               entertainment_tab= page.get_by_role("link", name="मनोरञ्जन")
               entertainment_tab.click()
               page.wait_for_load_state("networkidle")
               news_list= page.locator("div.category").all()
               for news in news_list[:5]:
                title_link= news.locator(".category-description h2 a")
                title = title_link.inner_text()
                img_elem = news.locator(".category-image a figure img")
                image_url = img_elem.get_attribute("data-src") or img_elem.get_attribute("src")         
                author = news.locator(".author-name p a").inner_text()
                page.locator("#tickerWrapper").evaluate("el => el.style.display = 'none'")
                title_link.click()
                page.wait_for_load_state("networkidle")
                category_link= page.locator(".category-name a")
                category_link.wait_for(state="visible")
                category = category_link.inner_text()

                self.results["entertainment_news"].append(
                    {
                        "title": title,
                        "image_url": image_url,
                        "category": category,
                        "author": author
                    }
                )
                page.go_back()  
                page.wait_for_load_state("networkidle")

            except Exception as e:
                print(e)

            try:
              page.goto(self.url, wait_until="networkidle")
              burger_menu= page.locator("[data-bs-target='#burgerMenu']").first
              burger_menu.click()
              page.wait_for_load_state("networkidle")
              search_field= page.locator("input[id='searchNews']")
              search_field.fill("cartoon of the day")
              search_field.press("Enter")
              page.wait_for_load_state("networkidle")
              first_result = page.locator("div.news-list").first
              if first_result.is_visible():
                c_title = first_result.locator(".news-description h2 a").inner_text()
                img_locator= first_result.locator(".news-image img")
                c_image_url = img_locator.get_attribute("data-src") or img_locator.get_attribute("src") or "no-image"
                c_author = first_result.locator(".author-name").inner_text()
                self.results["cartoon_of_the_day"] = {
                    "title": c_title,
                    "image_url": c_image_url,
                    "author": c_author
                }



            except Exception as e:
                print(e)
            

            with open("output.json", "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print("Done! Check output.json file.")
            browser.close()

                

if __name__ == "__main__":
    scraper = EkantipurNewsScraper(headless=False)
    scraper.run()

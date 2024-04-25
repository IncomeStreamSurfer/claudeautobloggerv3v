import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import random

def get_sitemap_urls(sitemap_url):
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.text, 'xml')
    urls = []

    sitemap_tags = soup.find_all('sitemap')
    if sitemap_tags:
        for sitemap in sitemap_tags:
            sitemap_loc = sitemap.find('loc').text.strip()
            urls.extend(get_sitemap_urls(sitemap_loc))
    else:
        url_tags = soup.find_all('url')
        urls = [url.find('loc').text.strip() for url in url_tags if 'facebook' not in url.find('loc').text.strip()]

    return urls

def find_images(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    body = soup.find('body')
    if body:
        img_tags = body.find_all('img')
        image_urls = []
        for img in img_tags:
            src = img.get('src')
            if src and not is_excluded(src) and not is_facebook_link(src):
                image_urls.append(src)
        return random.sample(image_urls, min(3, len(image_urls)))
    else:
        return []

def is_excluded(url):
    excluded_keywords = ['logo', 'icon', 'avatar', 'profile', 'button', 'social']
    url_lower = url.lower()
    return any(keyword in url_lower for keyword in excluded_keywords)

def is_facebook_link(url):
    return 'facebook' in url.lower()

def main(sitemap_url, output_file):
    urls = get_sitemap_urls(sitemap_url)

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Page URL', 'Image URL'])

        for url in urls:
            images = find_images(url)
            for image_url in images:
                absolute_url = urljoin(url, image_url)
                writer.writerow([url, absolute_url])

    print(f"Image URLs and their corresponding page URLs have been saved to {output_file}")

if __name__ == '__main__':
    sitemap_url = 'https://isuit.it/sitemaps/google_sitemap_categories_brand_en.xml'
    output_file = 'image_urls.csv'
    main(sitemap_url, output_file)
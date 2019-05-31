# -*- coding: utf-8 -*-
from urllib.request import urlopen, Request
import requests
import urllib
import bs4  
import sys



flag_url = 'https://search.naver.com/search.naver?sm=tab_hty.top&where=post&query='
search_url = 'https://search.naver.com/search.naver'
blog_url = 'https://blog.naver.com'


def crawl_blog(url):
    '''
      crawl_blog : 블로그 검색 페이지에서 title 과 해당 블로그 url 추출 (한페이지만)
    '''
    req = Request(url)
    page = urlopen(req)
    html = page.read()
    soup = bs4.BeautifulSoup(html, features='lxml')
    # 포스팅 리스트 추출 
    blog_section = soup.find('div', class_='blog section _blogBase _prs_blg').find('ul').findAll('li')
    
    if not blog_section:
      print('검색 결과 없음')
      return 

    title_set = [] # 타이틀 저장 
    url_set = [] # 블로그 포스트 url 저장 
    content_set = []  # 블로그 포스트 본문 저장 

    for item in blog_section:
      a_tag = item.find('dl').find('a')
      title = a_tag.get('title')
      if not title:
        title = a_tag.text
      url_set.append(a_tag.get('href'))
      title_set.append(title)

    # print('title_set', title_set)  # 페이지의 타이트들 확인 가능 
    # print(url_set) # 페이지의 url들 확인 가능

    for url in url_set:
      content = get_content(url)
      print(content)
      print('--------------')
      if content is False:  # 대표적인 3가지 태그, 속성이 아닌경우 추출 불가 (일일히 다해줘야됨) => 대표적인 3가지만 함 => 웬만한거 다됨 
        continue
      content_set.append(get_content(url)) 


def get_content(url):
  flag = True
  req = Request(url)
  page = urlopen(req)
  html = page.read()
  soup = bs4.BeautifulSoup(html, features='lxml')
  content = soup.find('div', class_='se_component_wrap sect_dsc __se_component_area')

  if not content:
    links = soup.select('iframe#mainFrame')
    for link in links:
      url = blog_url + str(link.get('src'))
      req = requests.get(url)
      html = req.text
      soup = bs4.BeautifulSoup(html, features='lxml')
      post_tag_results = soup.select('div#postViewArea')
      if post_tag_results:
        content = ''
        for item in post_tag_results:
          if item.text:
            content += str(item.text)

      else:
        results = soup.find('div', id='postListBody')

        if not results:
          flag = False
          break

        conset = results.findAll('div', class_='se-module se-module-text')
        content = ''

        for item in conset:
          if item.text:
            content += str(item.text)


  if flag is False or content is None:  # 대표적인 3가지가 아닌경우 False 반환 
    return False

  clean_content = content.strip()
  return clean_content


def get_next_page(url):
    '''
      다음 페이지를 호출하는 함수 
    '''
    req = Request(url)
    page = urlopen(req)
    html = page.read()
    soup = bs4.BeautifulSoup(html, features='lxml')
    paging = soup.find('div', class_='paging').findAll('a')
    
    if not paging: # 마지막 페이지를 의미
      print('over')
      return False

    cur_page = soup.find('div', class_='paging').find('strong').text
    for page in paging:
      if len(page.text) < 5: # TODO : 현재는 글자 길이로 판별하지만 만약 100000 이상 페이지를 가진다면 아스키 코드로 판별 
        if int(page.text) == int(cur_page) + 1:
          next_page_url = page.get('href')
          break
    return next_page_url
    


if __name__ == '__main__':
  '''
     // Usage //
     python3 crawl_blog.py 맥북-프로-신형 
    => 띄워쓰기 대신 '-' 기호를 사용해주세요  
  '''
  query = sys.argv[1] # format "맥북-프로-신형"
  query = str(query).replace('-', ' ')
  parse_query= urllib.parse.quote(query)    
  target_url = flag_url + parse_query

  while True:
    crawl_blog(target_url)
    target_url = get_next_page(target_url)
    if  target_url is False:
      break
    target_url = search_url + target_url

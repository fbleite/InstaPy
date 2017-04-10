"""Module that handles the like features"""
from math import ceil
from time import sleep
from re import findall
from selenium.webdriver.common.keys import Keys


def get_links_for_tag(browser, tag, amount, media=None):
  """Fetches the number of links specified
  by amount and returns a list of links"""
  if media is None:
    # All known media types
    media = ['', 'Post', 'Video']
  elif media == 'Photo':
    # Include posts with multiple images in it
    media = ['', 'Post']
  else:
    # Make it an array to use it in the following part
    media = [media]

  browser.get('https://www.instagram.com/explore/tags/'
              + (tag[1:] if tag[:1] == '#' else tag))
  sleep(2)

  # clicking load more
  body_elem = browser.find_element_by_tag_name('body')
  sleep(2)

  load_button = body_elem.find_element_by_xpath \
    ('//a[contains(@class, "_8imhp _glz1g")]')
  body_elem.send_keys(Keys.END)
  sleep(2)

  load_button.click()

  body_elem.send_keys(Keys.HOME)
  sleep(1)

  # Get links
  main_elem = browser.find_element_by_tag_name('main')
  link_elems = main_elem.find_elements_by_tag_name('a')
  total_links = len(link_elems)
  links = [link_elem.get_attribute('href') for link_elem in link_elems
           if link_elem.text in media]
  filtered_links = len(links)

  while (filtered_links < amount):
    amount_left = amount - filtered_links
    # Average items of the right media per page loaded
    new_per_page = ceil(12 * filtered_links / total_links)
    if new_per_page == 0:
      # Avoid division by zero
      new_per_page = 1. / 12.
    # Number of page load needed
    new_needed = int(ceil(amount_left / new_per_page))

    for _ in range(new_needed):  # add images x * 12
      body_elem.send_keys(Keys.END)
      sleep(1)
      body_elem.send_keys(Keys.HOME)
      sleep(1)

    link_elems = main_elem.find_elements_by_tag_name('a')
    total_links = len(link_elems)
    links = [link_elem.get_attribute('href') for link_elem in link_elems
             if link_elem.text in media]
    filtered_links = len(links)

  return links[:amount]


def check_link(browser, link, dont_like, ignore_if_contains, username):
  browser.get(link)
  sleep(2)

  """Check if the Post is Valid/Exists"""
  post_page = browser.execute_script("return window._sharedData.entry_data.PostPage")
  if post_page is None:
    print('Unavailable Page: ' + link)
    return False, 'Unavailable Page'

  """Gets the description of the link and checks for the dont_like tags"""
  is_video = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.is_video")
  user_name = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.owner.username")
  image_text = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.caption")

  """If the image has no description gets the first comment"""
  if image_text is None:
    image_text = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.comments.nodes[0].text")
  if image_text is None:
    image_text = "No description"

  print('Image from: ' + user_name)
  print('Link: ' + link)
  print('Description: ' + image_text)

  for word in ignore_if_contains:
    if word in image_text:
      return False, user_name, is_video

  for tag in dont_like:
    if tag in image_text or user_name == username:
      return True, user_name, is_video

  return False, user_name, is_video


def like_image(browser):
  """Likes the browser opened image"""
  like_elem = browser.find_elements_by_xpath("//a[@role = 'button']/span[text()='Like']")
  liked_elem = browser.find_elements_by_xpath("//a[@role = 'button']/span[text()='Unlike']")

  if len(like_elem) == 1:
    browser.execute_script("document.getElementsByClassName('" + like_elem[0].get_attribute("class") + "')[0].click()")
    print('--> Image Liked!')
    sleep(2)
    return True
  elif len(liked_elem) == 1:
    print('--> Already Liked!')
    return False
  else:
    print('--> Invalid Like Element!')
    return False


def get_tags(browser, url):
  """Gets all the tags of the given description in the url"""
  browser.get(url)
  sleep(1)

  image_text = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.caption")

  tags = findall(r'#\w*', image_text)
  return tags

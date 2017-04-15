"""Module that handles the like features"""
from math import ceil
from time import sleep
from re import findall
from selenium.webdriver.common.keys import Keys

def get_links_for_tag(browser, tag, amount):
  """Fetches the number of links specified
  by amount and returns a list of links"""
  browser.get('https://www.instagram.com/explore/tags/'
              + (tag[1:] if tag[:1] == '#' else tag))

  sleep(2)

  # clicking load more till there are 1000 posts
  body_elem = browser.find_element_by_tag_name('body')

  sleep(2)

  load_button = body_elem.find_element_by_xpath \
    ('//a[contains(@class, "_8imhp _glz1g")]')
  body_elem.send_keys(Keys.END)
  sleep(2)

  load_button.click()

  body_elem.send_keys(Keys.HOME)
  sleep(1)

  main_elem = browser.find_element_by_tag_name('main')

  new_needed = int(ceil((amount - 33) / 12))

  for _ in range(new_needed):  # add images x * 12
    body_elem.send_keys(Keys.END)
    sleep(1)
    body_elem.send_keys(Keys.HOME)
    sleep(1)

  link_elems = main_elem.find_elements_by_tag_name('a')
  links = [link_elem.get_attribute('href') for link_elem in link_elems]

  return links[:amount]

def check_link(browser, link, dont_like,
               ignore_if_contains, ignore_users,
               username):
  browser.get(link)
  sleep(2)

  """Check if the Post is Valid/Exists"""
  post_page = browser.execute_script("return window._sharedData.entry_data.PostPage")
  if post_page is None:
    print('Unavailable Page: ' + link)
    return False, 'Unavailable Page'

  """Gets the description of the link and checks for the dont_like tags"""
  user_name = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.owner.username")
  image_text = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.caption")

  owner_comments = browser.execute_script('''
    latest_comments = window._sharedData.entry_data.PostPage[0].media.comments.nodes;
    console.log(latest_comments);
    console.info('latest_comments was of type: ' + typeof(latest_comments));
    if (latest_comments === undefined) latest_comments = Array();
    console.info('latest_comments is now of type: ' + typeof(latest_comments));
    console.log(latest_comments);
    owner_comments = latest_comments
      .filter(item => item.user.username == '{}')
      .map(item => item.text)
      .reduce((item, total) => item + '\\n' + total, '');
    return owner_comments;
  '''.format(username))
  if owner_comments == '':
    owner_comments = None

  """Append owner comments to description as it might contain further tags"""
  if image_text is None:
    image_text = owner_comments
  elif owner_comments is not None:
    image_text = image_text + '\n' + owner_comments

  """If the image still has no description gets the first comment"""
  if image_text is None:
    image_text = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.comments.nodes[0].text")
  if image_text is None:
    image_text = "No description"

  print('Image from: ' + user_name)
  print('Link: ' + link)
  print('Description: ' + image_text)

  """Check if the user_name is in the ignore_users list"""
  if (user_name in ignore_users) or (user_name == username):
    print('--> Ignoring user: ' + user_name)
    return True, user_name

  if any((word in image_text for word in ignore_if_contains)):
      print('--> Ignoring content: ' + tag)
      return False, user_name

  if any((tag in image_text for tag in dont_like)):
      return True, user_name

  return False, user_name

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

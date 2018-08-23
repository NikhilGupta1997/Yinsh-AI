#communicates with the js file using selenium to integrate the yinsh sim and the client -server architecture

from selenium import webdriver

driver = webdriver.Firefox()
# we'll have to make this relative to work for everyone
absPath = os.path.abspath("Yinsh.html")
driver.get("file:"+absPath)

el=driver.find_elements_by_id("PieceLayer")

action = webdriver.common.action_chains.ActionChains(driver)
action.move_to_element_with_offset(el[0], 438, 438)
action.click()
action.perform()


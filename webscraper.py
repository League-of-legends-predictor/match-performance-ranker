import logging
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# define global parameters
default_time_out = 30 # default time_out
used_summoners = [] # summoners already used as seeds
goal_num_samples_per_summoner = 150
min_samples_per_tier = 10000
file_path = '' # only declare file path here as a global, set it in main
total_samples = 0; iron_samples =0; bronze_samples =0;  silver_samples =0; gold_samples =0; plat_samples =0; diamond_samples =0

past_samples = []


# start timer
main_start = time.perf_counter()

def waitForClassToLeave(driver, c):
    try:
        loading = driver.find_element(By.CLASS_NAME, c).is_displayed()
        while(loading):
            loading = driver.find_element(By.CLASS_NAME, c).is_displayed()
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except: # class doesnt exist so just return
        return

# loads more matches onto page, returns True if was able to load more matches, False if not
def loadMoreMatches(driver):
    try:
        more_btn_xp = '//*[@id="content-container"]/div[2]/button'
        more_btn =  driver.find_element(By.XPATH,more_btn_xp)
        more_btn.click()
        # WAIT! for matches to load
        loading_icon_class = 'css-151wajb.e1mnv9ea0'
        waitForClassToLeave(driver, loading_icon_class)
        return True
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        return False


def submitSample(sample):
    # add to past samples
    global past_samples
    past_samples.append(sample)
    # add to all samples
    with open(file_path, 'a') as f:
            f.write("|".join(str(item) for item in sample))
            f.write('\n')

# returns number of good_samples found in the match
def analyseMatch(match, target_tier,  num_samples_so_far):
    submitted_samples = []
    try:
        match_type = match.find_element(By.CLASS_NAME, 'type').text
        # WAIT! for detail btn to load
        WebDriverWait(match, default_time_out).until(EC.element_to_be_clickable((By.CLASS_NAME,'detail')))
        # open match details
        detail_btn = match.find_element(By.CLASS_NAME, "detail")
        detail_btn.click()
        
        # WAIT! for match details to load
        overview_class = 'css-1dm3230.eo0wf2y0' 
        WebDriverWait(match, default_time_out).until(EC.presence_of_element_located((By.CLASS_NAME,overview_class)))
        
        # get match overview
        overview_div = match.find_element(By.CLASS_NAME, overview_class)
        # find rows containing samples
        rows = overview_div.find_elements(By.TAG_NAME, 'tr')
        # delete 2 rows, as they never contain samples
        del rows[0]; del rows[5]; 
        
        # a row has our sample info
        for row_num, row in enumerate(rows):
            try:
                # get sample data
                sample = row.text
                sample = sample.split("\n")
                # example sample =  ['13', 'aubmlk', 'Iron 2', '4.7', '9th', '2/4/0 (5%)', '0.50:1', '10,090', '19,694', '0', '4 / 0', '95', '3.9/m']

                # check some sample data
                tier = sample[2]
                kp = sample[5][-4:]
                afk_or_troll = kp == '(0%)'
            
                if(not afk_or_troll and (target_tier in tier or target_tier is None)):
                    # encode name so it can work in txt file
                    sample[1] = sample[1].encode('utf-8').decode('Latin1')
                    # append match type
                    sample.append(match_type)
                    # append role to sample
                    role = row_num%5 
                    sample.append(str(role))
                    # check not duplicate sample
                    global past_samples
                    if(sample not in past_samples):
                        # submit sample
                        submitSample(sample=sample)
                        submitted_samples.append(sample)
                    if ((len(submitted_samples)+num_samples_so_far) >= goal_num_samples_per_summoner):
                        return submitted_samples
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                pass
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        pass
    return submitted_samples

def getElegibleMathces(matches, start):
    elegible_matches = []
    past_the_elegible = False
    for match in matches[start:]:
        try:
            match_type = match.find_element(By.CLASS_NAME, 'type').text

            result = match.find_element(By.CLASS_NAME, "result").text
            time_stamp = match.find_element(By.CLASS_NAME, "time-stamp").text
            tmp = time_stamp.split(" ")

             # 'a' -> '1'
            if(tmp[0] == 'a'):
                tmp[0] = '1'

            # check not past limit
            if(tmp[1] == 'months'):
                if(int(time_stamp[0]) > 2):
                    past_the_elegible = True
                    return past_the_elegible, elegible_matches

            # check we're in right months and result was not a Remake
            if((time_stamp== 'a month ago' or time_stamp == '2 months ago') and result != 'Remake' and match_type =='Ranked Solo'):
                elegible_matches.append(match)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            pass
    return past_the_elegible, elegible_matches

# recursive function that will keep extracting samples until no more needed/left
def extractSamples(driver, start, num_samples_so_far, target_tier):
    samples = []
            
    # go to ranked queue
    ranked_btn_xpath = '//*[@id="content-container"]/div[2]/div[1]/ul/li[2]/button'
    # WAIT! for ranked btn to be clickable
    WebDriverWait(driver, default_time_out).until(EC.element_to_be_clickable((By.XPATH, ranked_btn_xpath)))
    ranked_btn = driver.find_element(By.XPATH,ranked_btn_xpath)
    ranked_btn.click()
    # WAIT! for matches to load
    loading_icon_class = 'css-151wajb.e1mnv9ea0'
    waitForClassToLeave(driver, loading_icon_class)

    # find matches
    matches_table_xp = '//*[@id="content-container"]/div[2]/div[3]'
    WebDriverWait(driver, default_time_out).until(EC.presence_of_element_located((By.XPATH, matches_table_xp)))
    matches_table = driver.find_element(By.XPATH, matches_table_xp)
    matches = matches_table.find_elements(By.CLASS_NAME, "css-1qq23jn.e1iiyghw3")
    next_start = len(matches)
    enough_samples = False 
    # find elegible matches
    past_the_elegible, matches = getElegibleMathces(matches, start)

    # analyse elegible matches
    tmp = num_samples_so_far
    for match in matches:
        print(f"Summoner Samples: {tmp}/{goal_num_samples_per_summoner}")
        # check if enough samples  
        enough_samples = tmp >= goal_num_samples_per_summoner
        if (enough_samples):
            print('Enough Samples')
            return samples
        # get samples from match
        samples = samples + analyseMatch(match=match, target_tier=target_tier, num_samples_so_far=tmp)
        tmp = len(samples) + num_samples_so_far
        
    # check if we can load more
    if(not past_the_elegible):
        print("Loading more matches, not enough samples")
        num_samples_so_far = tmp
        # load more matches
        could_load = loadMoreMatches(driver=driver)
        # check if more matches loaded
        if(could_load):
            # get new start index
            start = next_start
            # enter recursion with new start index
            samples = samples + extractSamples(driver=driver, start=start, num_samples_so_far=num_samples_so_far, target_tier=target_tier)
            return samples
    print('Could not load more matches, moving to next summoner')
    return samples
            
def findFromBackup(target_tier):
    # get available samples from all past samples in current tier
    global past_samples
    available_samples = past_samples.copy()
    with open('errors.txt', 'a') as f:
            f.write(f'When searching for {target_tier}, needed to search from backup\n')
    # find unused name
    while True:
        random_sample = random.choice(available_samples)
        name = random_sample[1]
        available_samples.remove(random_sample)
        if(not (name in used_summoners) or len(available_samples)<=0):
            break
    # if name has been used, return nothing because there is nothing to return (this shouldn't happen though...)
    if(name in used_summoners):
        with open('errors.txt', 'a') as f:
            f.write(f'When searching for {target_tier}, no username found from backup -> No more samples to find\n')
            return None
    with open('errors.txt', 'a') as f:
        f.write(str(random_sample))
        f.write('\n')
        f.write(f'Found: {name}\n')
    return name
        
def findNextSummoner(samples, target_tier):
    # if we have any samples to choose from
    if(len(samples)>0):
        # copy available samples
        available_samples = samples.copy()
        # find unused name
        while True:
            random_sample = random.choice(available_samples)
            name = random_sample[1]
            name = name.encode('Latin1').decode('utf-8')
            available_samples.remove(random_sample)
            if(not (name in used_summoners) or len(available_samples)<=0):
                break
        # if we couldn't find an unused name, get name from backup
        if(name in used_summoners):
            return findFromBackup(target_tier)
        # otherwise we can return unused name
        return name
    else: # find an unnused name from backup
        return findFromBackup(target_tier)

def scrapeCurrentPage(driver, target_tier):
    num_samples = 0; next_summoner = None

    start = 0
    samples = []
    
    samples = extractSamples(driver=driver, start=start, num_samples_so_far=num_samples, target_tier=target_tier)

    num_samples = len(samples); next_summoner = findNextSummoner(samples, target_tier)
    # if no next summoner was found (shouldn't happen but backup failed)
    if(next_summoner == None):
        msg = f'No New Summoner Was Found When Looking For {target_tier}'
        with open('errors.txt', 'a') as f:
                f.write(msg)
                f.write('\n')

    used_summoners.append(next_summoner)
    return num_samples, next_summoner


def incrementGlobal(target_tier, num_samples):
    global iron_samples, bronze_samples, silver_samples, gold_samples, plat_samples, diamond_samples
    if(target_tier== 'Iron'):
        iron_samples+=num_samples
    if(target_tier== 'Bronze'):
       bronze_samples +=num_samples
    if(target_tier== 'Silver'):
        silver_samples+=num_samples
    if(target_tier == 'Gold'):
        gold_samples+=num_samples
    if(target_tier== 'Plat'):
        plat_samples+=num_samples
    if(target_tier== 'Diamond'):
        diamond_samples+=num_samples


def runScraper(driver, seed_summoner, target_tier, min_samples):
    global past_samples
    if len(past_samples)>0:
        print(f'Found Past {target_tier} Samples')
    else:
        print(f'No Past {target_tier} Samples')
    
    start = time.perf_counter()
    total_samples_this_tier = 0
    # first current summoner is the seed summoner
    current_summoner = seed_summoner
    # go to summoners page
    print('Summoner Page Loading')
    driver.get(f'https://www.op.gg/summoners/euw/{current_summoner}')
    #accept cookies 
    print('Waiting for cookie pop-up')
    try:
        cookie_btn_xp = '//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]'
        # WAIT! for cookies to come up
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, cookie_btn_xp)))
        cookie_btn = driver.find_element(By.XPATH,cookie_btn_xp)
        cookie_btn.click()
        print('Clicked cookie pop-up')
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        print("No cookie pop-up")

    while(total_samples_this_tier < min_samples):
        start_inner = time.perf_counter()
        print(f"Getting samples from seed summoner '{current_summoner}', Target Tier: {target_tier}")

        # Deal With current Page
        num_samples, next_summoner = scrapeCurrentPage(driver=driver, target_tier=target_tier)
        end = time.perf_counter()
        total_samples_this_tier+=num_samples
        global total_samples
        total_samples+=num_samples

        incrementGlobal(target_tier, num_samples)
        # Output current situation
        print(f"Total Samples Found: {total_samples}\n(Bronze: {bronze_samples}/{min_samples_per_tier}), (Silver: {silver_samples}/{min_samples_per_tier}), (Gold: {gold_samples}/{min_samples_per_tier})\n(Plat: {plat_samples}/{min_samples_per_tier}), (Diamond: {diamond_samples}/{min_samples_per_tier}), (Iron: {iron_samples}/{min_samples_per_tier})")
        print(f'Time Spent... Summoner: {end-start_inner:0.2f}s \tTier: {end-start:0.2f}s \tTotal: {end-main_start:0.2f}s')

        # Check if we should return
        if(next_summoner == None or num_samples>=min_samples):
            return int(total_samples_this_tier)
        current_summoner = next_summoner
        print('\nNew Summoner Page Loading...')
        driver.get(f'https://www.op.gg/summoners/euw/{current_summoner}')
        
    return total_samples_this_tier


# init driver
options = webdriver.ChromeOptions() 
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument('headless')
caps = webdriver.DesiredCapabilities.CHROME.copy()
caps['acceptInsecureCerts'] = True
caps['acceptSslCerts'] = True
service_obj = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service_obj, desired_capabilities=caps, options=options)


# Get Bronze Samples - Joker of Jukes
bronze_complete = False
try:
    file_path = 'raw_samples/bronze.txt'
    # load past samples
    past_samples = []
    print('Loading past Bronze samples')
    with open(file_path, 'r') as f:
        for line in f.readlines():
            sample = line[:-1].split('|')
            past_samples.append(sample)
    target_tier = 'Bronze'
    bronze_samples=runScraper(driver=driver, seed_summoner='Joker of Jukes', target_tier=target_tier, min_samples=min_samples_per_tier)
    bronze_complete = True
except KeyboardInterrupt:
    raise KeyboardInterrupt
except Exception as e:
    msg = 'Error when Scraping Bronze Samples:\n'
    error_string = str(e)
    with open('errors.txt', 'a') as f:
            f.write(msg)
            f.write(error_string)
            f.write('\n')

# Get Silver Samples - TheTorii
silver_complete = False

try:
    file_path = 'raw_samples/silver.txt'
    # load past samples
    past_samples = []
    print('Loading past Silver samples')
    with open(file_path, 'r') as f:
        for line in f.readlines():
            sample = line[:-1].split('|')
            past_samples.append(sample)
    target_tier = 'Silver'
    silver_samples=runScraper(driver=driver, seed_summoner='TheTorii', target_tier=target_tier, min_samples=min_samples_per_tier)
    silver_complete = True
except KeyboardInterrupt:
    raise KeyboardInterrupt
except Exception as e:
    msg = 'Error when Scraping Silver Samples:\n'
    error_string = str(e)
    with open('errors.txt', 'a') as f:
            f.write(msg)
            f.write(error_string)
            f.write('\n')

# Get Gold Samples - The God of Memes
gold_complete = False

try:
    file_path = 'raw_samples/gold.txt'
    # load past samples
    past_samples = []
    print('Loading past Gold samples')
    with open(file_path, 'r') as f:
        for line in f.readlines():
            sample = line[:-1].split('|')
            past_samples.append(sample)
    target_tier = 'Gold'
    gold_samples=runScraper(driver=driver, seed_summoner='The God of Memes', target_tier=target_tier, min_samples=min_samples_per_tier)
    gold_complete = True
except KeyboardInterrupt:
    raise KeyboardInterrupt
except Exception as e:
    msg = 'Error when Scraping Gold Samples:\n'
    error_string = str(e)
    with open('errors.txt', 'a') as f:
            f.write(msg)
            f.write(error_string)
            f.write('\n')

# Get Plat Samples - 0Ld Pro Hasagi
plat_complete = False
try:
    file_path = 'raw_samples/plat.txt'
    # load past samples
    past_samples = []
    print('Loading past Plat samples')
    with open(file_path, 'r') as f:
        for line in f.readlines():
            sample = line[:-1].split('|')
            past_samples.append(sample)
    target_tier = 'Plat'
    plat_samples=runScraper(driver=driver, seed_summoner='0Ld Pro Hasagi', target_tier=target_tier, min_samples=min_samples_per_tier)
    plat_complete = True
except KeyboardInterrupt:
    raise KeyboardInterrupt
except Exception as e:
    msg = 'Error when Scraping Plat Samples:\n'
    error_string = str(e)
    with open('errors.txt', 'a') as f:
            f.write(msg)
            f.write(error_string)
            f.write('\n')

# Get Diamond Samples - Darwin at Work
diamond_complete = False
try:
    file_path = 'raw_samples/diamond.txt'
   # load past samples
    past_samples = []
    print('Loading past Diamond samples')
    with open(file_path, 'r') as f:
        for line in f.readlines():
            sample = line[:-1].split('|')
            past_samples.append(sample)
    target_tier = 'Diamond'
    diamond_samples=runScraper(driver=driver, seed_summoner='Darwin at Work', target_tier=target_tier, min_samples=min_samples_per_tier)
    diamond_complete = True
except KeyboardInterrupt:
    raise KeyboardInterrupt
except Exception as e:
    msg = 'Error when Scraping Diamond Samples:\n'
    error_string = str(e)
    with open('errors.txt', 'a') as f:
            f.write(msg)
            f.write(error_string)
            f.write('\n')


# Get Iron Samples - aubmlk
iron_complete = False
try:
    file_path = 'raw_samples/iron.txt'
    # load past samples
    past_samples = []
    print('Loading past Iron samples')
    with open(file_path, 'r') as f:
        for line in f.readlines():
            sample = line[:-1].split('|')
            past_samples.append(sample)
    target_tier = 'Iron'
    iron_samples=runScraper(driver=driver, seed_summoner='aubmlk', target_tier=target_tier, min_samples=min_samples_per_tier)
    iron_complete = True
except KeyboardInterrupt:
    raise KeyboardInterrupt
except Exception as e:
    msg = 'Error when Scraping Iron Samples:\n'
    error_string = str(e)
    with open('errors.txt', 'a') as f:
            f.write(msg)
            f.write(error_string)
            f.write('\n')


# wrap up
main_end = time.perf_counter()
print("Scraper Complete")
no_errors = iron_complete and bronze_complete and silver_complete and gold_complete and plat_complete and diamond_complete
print('No Errors: ', no_errors)
print(f'Total Time Elapsed: {main_end-main_start:0.2f}s')

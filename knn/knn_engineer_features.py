def engineerSample(sample):
    ######### extract useful data ############

    end_lvl = int(sample[0]); tier = sample[2]; op_score = float(sample[3])
    kda_kp = sample[5];  dmg_done = sample[7]; dmg_taken = sample[8]
    cw = int(sample[9]); wp_wk = sample[10]; cs = int(sample[11]); cs_m = sample[12]; position = int(sample[-1])
    
    ########### convert into right format ##########
    # convert tier into right format
    tier = tier.split(' ')[0]
    if tier == 'Iron':
        tier = 0
    elif tier == 'Bronze':
        tier = 1
    elif tier =='Silver':
        tier = 2
    elif tier =='Gold':
        tier = 3
    elif tier =='Platinum':
        tier = 4
    elif tier =='Diamond':
        tier = 5
    else: # error, shouldnt happen but good to check
        print(tier)
        return []

    # convert kda into right format
    kda_kp = kda_kp.split(" ") # '1/2/3 (20%)' -> ['1/2/3', '(20%)']
    kda = kda_kp[0]; 
    kda = kda.split('/')
    kills = int(kda[0]) +1; deaths = int(kda[1]) +1; assists = int(kda[2]) +1
    # convert kill particpation into right format
    kp = kda_kp[1]
    kill_participation = int(kp[1:-2])/100
    # convert dmg stats into right format
    dmg_done = int(dmg_done.replace(',', ''))
    dmg_taken = int(dmg_taken.replace(',', ''))
    # convert ward stats into right format
    wp_wk = wp_wk.replace(' ', '')
    wp_wk = wp_wk.split('/')
    wp = int(wp_wk[0]); wk = int(wp_wk[1])
    # convert cs/m into right format
    cs_m = float(cs_m[:-2])

    ############ check validity ###############
    if(cs_m==0 or dmg_done==0 or dmg_taken==0):
        print(sample)
        return []

    ############ engineered features ###########
    # new simple features
    minutes = round(cs/cs_m)
    
    takedowns = kills + assists
    # calculate "positive_impact", a feature to try calculate how well they played
    weight = 250
    positive_impact = kills*weight/2 + assists*weight/3 + cs*weight/20 + wk*weight/40

    # ratio features
    kpd = kills/deaths
    apd = assists/deaths
    tpd = takedowns/deaths 
    dtr = dmg_done/dmg_taken 

    # bonus features
    dmg_surplus = dmg_done-dmg_taken
    ward_advantage = wp+wk

    ########### combine features to make new smaple ################

    engineered_sample = [
        # game info
        kill_participation,
        #op_score/minutes,
        tpd/minutes,
        positive_impact/minutes,

        # Output/Result
        tier
    ]
    return engineered_sample

# read a text file as a 2d array
sources = ['iron.txt','bronze.txt','silver.txt','gold.txt','plat.txt','diamond.txt']
for src in sources:
    samples= []
    print(f'Reading {src}')
    with open('raw_samples/'+src, 'r') as f:
        for line in f.readlines():
                samples.append(line.split('|'))

    print(f'Engineering {src}')
    dest = 'knn/knn_samples.txt'
    for sample in samples:
        sample = engineerSample(sample)
        if (sample != []):
            with open(dest, 'a') as f:
                f.write(",".join(str(item) for item in sample))
                f.write('\n')

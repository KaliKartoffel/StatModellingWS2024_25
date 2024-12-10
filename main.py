import random
import math
from collections import deque
import numpy as np

class Emergency:
        district = None
        start_time = None
        prio = None
        def __init__(self, district, start_time, prio):
            self.district = district
            self.start_time = start_time
            self.prio = prio

class EmergencySimulator:
    populations = [10000, 35000, 25000, 25000, 15000, 20000, 45000, 40000, 15000, 35000]
    avg_travel_times = [
    [3, 6, 5, 8, 8, 4, 6, 8, 10, 12],
    [6, 4, 5, 8, 14, 6, 4, 10, 7, 6],
    [5, 5, 3, 6, 10, 8, 8, 12, 12, 7],
    [8, 8, 6, 5, 6, 10, 13, 9, 10, 11],
    [8, 14, 10, 6, 5, 7, 9, 7, 10, 20],
    [4, 6, 8, 10, 7, 3, 5, 5, 9, 17],
    [6, 4, 8, 13, 9, 5, 3, 10, 7, 10],
    [8, 10, 12, 9, 7, 5, 10, 5, 14, 20],
    [10, 7, 12, 10, 10, 9, 7, 14, 7, 14],
    [12, 6, 7, 11, 20, 17, 10, 20, 14, 6],
    ]
    travel = { #including care_work
        "currently_traveling": False,
        "target": None,
        "start": None,
        "time_remaining": None,
        "time_total": None,
        "going_towards_hq_dist": None,
        "current_emergency": None,
        "currently_giving_care": False
    }
    current_dist = 1
    time_to_next_emergency = 0
    total_time_passed = 0
    total_time_doctor_used = 0
    total_time_doctor_center = 0
    waiting_times_non_life_threatening = None
    life_threatening_emergencies = None
    non_life_threatening_emergencies = None

    def __init__(self, seed = 123):
        random.seed(seed)
        self.waiting_times_non_life_threatening = list()
        self.life_threatening_emergencies = deque()
        self.non_life_threatening_emergencies = deque()

    def get_travel_time(self, dist1, dist2, dist3=None, ratio_traveled=0.5):
        # if between two districts is needed only supply dist1 and dist2, 
        # if currently underway between districts supply dist1 and dist2 as current route, dist3 as new and travel ratio
        if not dist3:
            avg_travel_time_sec = round(self.avg_travel_times[dist1][dist2]*60)
        else:
            avg_travel_time_sec = round(self.avg_travel_times[dist1][dist3]*60*ratio_traveled + self.avg_travel_times[dist2][dist3]*60*(1-ratio_traveled))

        return random.randint(round(avg_travel_time_sec*0.5), round(avg_travel_time_sec*1.5))
    
    def get_time_to_next_event(self):
        mean_interval_seconds = 50 * 60
        rate = 1.0 / mean_interval_seconds
        return round(random.expovariate(rate))

    def wait_secs(self, secs):

        self.total_time_passed += secs
        if self.travel["currently_traveling"]:
            self.travel["time_remaining"] -= secs
        self.time_to_next_emergency -= secs

        if not self.travel["currently_traveling"]:
            self.total_time_doctor_center += secs
            if len(self.non_life_threatening_emergencies) + len(self.life_threatening_emergencies) != 0:
                print("Broke smth ######################################################")
        elif not self.travel["going_towards_hq_dist"]:
            self.total_time_doctor_used += secs

    def start_new_travel(self, target_dist, emergency= None):
        if emergency:
            pass
        if self.travel["currently_traveling"]:
            dist1 = self.travel["start"]
            dist2 = self.travel["target"]
            dist3 = target_dist
            ratio_traveled = 1-(self.travel["time_remaining"]/self.travel["time_total"])

            my_time = self.get_travel_time(dist1, dist2, dist3, ratio_traveled)
            self.travel["time_total"] = my_time
            self.travel["time_remaining"] = my_time
            if ratio_traveled > 0.5:
                self.travel["start"] = dist2
            else:
                self.travel["start"] = dist1
            
        else:
            my_time = self.get_travel_time(self.current_dist, target_dist)
            self.travel["time_total"] = my_time
            self.travel["time_remaining"] = my_time
            self.travel["start"] = self.current_dist

        self.travel["currently_traveling"] = True
        self.travel["target"] = target_dist
        

        if emergency != None:
            self.travel["current_emergency"] = emergency
            self.travel["going_towards_hq_dist"] = False
        else:
            self.travel["current_emergency"] = None
            self.travel["going_towards_hq_dist"] = True ### NOTE: Change if not always going back to HQ if non emergency

        self.travel["currently_giving_care"] = False
        self.travel["care_time_remaining"] = None


    def generate_emergency(self):
        if self.time_to_next_emergency <= 0:
            self.time_to_next_emergency = self.get_time_to_next_event()
            if (random.choices([0, 1], weights=[3, 1])[0] == 1): #life threatening
                self.life_threatening_emergencies.append(Emergency(
                        district = random.choices(range(10), weights=self.populations)[0],
                        start_time = self.total_time_passed,
                        prio=1
                    ))
                if self.travel["currently_traveling"] and not self.travel["currently_giving_care"] and not self.travel["going_towards_hq_dist"] and self.travel["current_emergency"].prio == 0:
                    self.non_life_threatening_emergencies.appendleft(self.travel["current_emergency"])
                    em = self.life_threatening_emergencies.popleft()
                    self.start_new_travel(em.district, em)
            else:
                self.non_life_threatening_emergencies.append(Emergency(
                        district = random.choices(range(10), weights=self.populations)[0],
                        start_time = self.total_time_passed,
                        prio=0
                    ))
            
            if not self.travel["currently_traveling"] or self.travel["going_towards_hq_dist"]:
                self.move_to_next_em()

    def move_to_next_em(self):
        if len(self.life_threatening_emergencies) != 0:
            my_queue =  self.life_threatening_emergencies
        elif len(self.non_life_threatening_emergencies) != 0:
            my_queue =  self.non_life_threatening_emergencies
        else:
            self.start_new_travel(1) ### NOTE: Change for multiple HQs
            return
        em = my_queue.popleft()
        self.start_new_travel(em.district, em)

    def get_em_care_time(self, em):
        if em.prio == 1:
            return random.randint(30*60, 90*60)
        else:
            return random.randint(10*60, 20*60)

    def check_travel(self):
        if not self.travel["currently_traveling"]: 
            return
        if not self.travel["time_remaining"] <= 0:
            return
        if self.travel["going_towards_hq_dist"] == True:
            self.current_dist = 1
            self.travel["currently_traveling"] = False
            return
        if self.travel["currently_giving_care"]:
            #done with caregiving
            self.travel["currently_giving_care"] = False
            self.move_to_next_em()
        else:
            #start with caregiving
            em = self.travel["current_emergency"]
            if em.prio == 0:
                self.waiting_times_non_life_threatening += [self.total_time_passed - em.start_time]
            self.travel["time_remaining"] = self.get_em_care_time(em)
            self.travel["currently_giving_care"] = True
            self.current_dist = self.travel["target"]


    def simulate(self, total_time_hours=1):
        max_time = total_time_hours*3600
        while(self.total_time_passed < max_time):
            self.generate_emergency()
            self.check_travel()
            
            if self.travel["time_remaining"]:
                time_to_pass = min(self.travel["time_remaining"], self.time_to_next_emergency)
            else:
                time_to_pass = self.time_to_next_emergency

            self.wait_secs(time_to_pass)

        return {"doc_util": self.total_time_doctor_used/self.total_time_passed,
                "doc_center": self.total_time_doctor_center/self.total_time_passed,
                "avg_non_live_threatening_watiing_time_min": sum(self.waiting_times_non_life_threatening)/len(self.waiting_times_non_life_threatening)/60}

    def test(self):
        return self.simulate(500)
    

if __name__ == "__main__":
    doc_util_results = []
    doc_center_results = []
    waiting_results = []

    es = EmergencySimulator(seed=40)
    print(es.simulate(1000))

    for i in range(100):
        print("done:", i)
        es = EmergencySimulator(seed=i)
        result = es.simulate(1000)
        doc_util_results.append(result["doc_util"])
        doc_center_results.append(result["doc_center"])
        waiting_results.append(result["avg_non_live_threatening_watiing_time_min"])

    print(waiting_results)

    doc_util_average = np.mean(doc_util_results)
    doc_util_std_deviation = np.std(doc_util_results)

    doc_center_average = np.mean(doc_center_results)
    doc_center_std_deviation = np.std(doc_center_results)

    waiting_average = np.mean(waiting_results)
    waiting_std_deviation = np.std(waiting_results)

    print(f"Doc Util - Average: {doc_util_average}, Standard Deviation: {doc_util_std_deviation}")
    print(f"Doc Center - Average: {doc_center_average}, Standard Deviation: {doc_center_std_deviation}")
    print(f"Waiting Times - Average: {waiting_average}, Standard Deviation: {waiting_std_deviation}")
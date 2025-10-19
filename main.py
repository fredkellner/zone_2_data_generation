import os
import datetime

import pandas as pd
import garminconnect


email = os.getenv('email')
password = os.getenv('garmin_pw')
birthday = os.getenv('birthday')

garmin = garminconnect.Garmin(email, password)
garmin.login()

def compute_maf_hr_on_birthdate(birth_date:str):
  """Computes Zone 2 HR using Phil Maffetone's Zone 2 heart rate equation"""
  try:
    birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
  except ValueError:
    raise
  years_old = int((datetime.datetime.today() - birth_date_obj).days / 365.25)
  return = 180 - years_old

def compute_acitivity_duration(activity):
   end_activity = int(activity['beginTimestamp'] + (activity['duration']*1000))
   duration = (
        datetime.datetime.fromtimestamp(end_activity/1000) 
     - datetime.datetime.fromtimestamp(activity['beginTimestamp']/100).seconds  // 60 % 60
  
  

temp_df_list = []
for subtract_day in (range(0, datetime.datetime.today().timetuple().tm_yday)):
  start_date = (datetime.datetime.today() - datetime.timedelta(days=subtract_day)).strftime("%Y-%m-%d")
  activities = garmin.get_activities_by_date(start_date, start_date)
  for activity in activities:
    activityID = str(activity['activityId'])
    activty_type = activity['activityType']['typeKey']
    begin_activity = activity['beginTimestamp']
    end_activity = int(activity['beginTimestamp'] + (activity['duration']*1000))
    duration = (
        datetime.datetime.fromtimestamp(end_activity/1000) -datetime.datetime.fromtimestamp(begin_activity/1000)
        ).seconds  // 60 % 60

    # skip activities that are less than 10 minutes to
    # account for errors in starting watch. 
    if duration < 10:
      continue
    else:
      details = garmin.get_activity_details(activityID)
      temp_hr_list = []
      timestamp_list = []
      activity = details.get('activityDetailMetrics')
      index_stuff = details.get('metricDescriptors')
      for metric in activity:
        for val in index_stuff:
          if val['key'] == 'directHeartRate':
            hr_index = val['metricsIndex']
            temp_hr_list.append(metric['metrics'][hr_index])
          if val['key'] == 'directTimestamp':
            time_index = val['metricsIndex']
            timestamp_list.append(metric['metrics'][time_index])
      hr_val_df = pd.DataFrame(zip(timestamp_list, temp_hr_list), columns=['timestamp', 'hr'])
      hr_val_df['activityID'] =  activityID
      hr_val_df['duration_in_minutes'] = duration
      hr_val_df['date'] = start_date
      hr_val_df['activity'] = activty_type
      temp_df_list.append( hr_val_df)
      del( hr_val_df)

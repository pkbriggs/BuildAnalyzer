from datetime import datetime
import sys

"""
This script will output some useful stats regarding timestamps. It makes the assumption that the provided file is a text file with the following format:

START: 08/29/16 16:52:14
FINISH: 08/29/16 16:54:14
START: 08/29/16 17:02:01
FINISH: 08/29/16 17:03:11
...etc..

Thus, the file should contain alternating lines that start with 'START:' and 'FINISH:', followed by the proper date and time. The time format can be customized with the TIME_FORMAT variable below.

It will output the total number of builds, average build time, and the total time spent waiting for builds (all showing overall stats and just stats for today). TODO: Add ability to show efficiency thoughout day.
"""

BUILD_TIME_FILE = "buildtimes"
TIME_FORMAT = "%m/%d/%y %H:%M:%S"
SECONDS_IN_DAY = 86400
SECONDS_IN_HOUR = 3600
SECONDS_IN_MINUTE = 60
SECONDS_IN_WORK_DAY = 28800 # assuming an 8 hour day

def get_average(nums):
  total = 0.0
  for num in nums:
    total += num
  if len(nums) > 0:
    return total / len(nums)
  return 0

def get_seconds_from_data(times):
  total = 0.0
  for time in times:
    total += time
  return total

def get_time_string_from_seconds(total):
  numDays = 0
  numHours = 0
  numMinutes = 0
  numSeconds = 0
  
  if total > SECONDS_IN_DAY:
    numDays += int(total)/SECONDS_IN_DAY
    total %= SECONDS_IN_DAY
    numDays += 1
  if total > SECONDS_IN_HOUR:
    numHours += int(total)/SECONDS_IN_HOUR
    total %= SECONDS_IN_HOUR
  if total > SECONDS_IN_MINUTE:
    numMinutes += int(total)/SECONDS_IN_MINUTE
    total %= SECONDS_IN_MINUTE
  numSeconds = int(total)

  output = ""
  if numDays > 0:
    output += str(numDays)
    if numDays == 1:
      output += " day, "
    else:
      output += " days, "

  if numHours > 0:
    output += str(numHours)
    if numHours == 1:
      output += " hour, "
    else:
      output += " hours, "

  if numMinutes > 0:
    output += str(numMinutes)
    if numMinutes == 1:
      output += " minute, "
    else:
      output += " minutes, "

  # Always include number of seconds
  output += str(numSeconds)
  if numSeconds == 1:
    output += " second "
  else:
    output += " seconds "

  return output

def get_efficiency_percent(days):
  totalEfficiency = 0.0
  for day in days:
    totalEfficiency += get_day_efficiency_percent(days[day])
  totalEfficiency /= len(days)
  return totalEfficiency
    
def get_day_efficiency_percent(times):
  totalSeconds = 0.0
  for time in times:
    totalSeconds += time
  return 100 - (totalSeconds / SECONDS_IN_WORK_DAY * 100)


class BuildTimeAnalyzer():
  def __init__(self):
    self.buildTimeFile = open(BUILD_TIME_FILE, "r")
    self.times = []
    self.days = {}
    self.processedStartTime = False
    self.startTime = None

  def logTime(self, startTime, endTime):
    startDate = datetime.strptime(startTime, TIME_FORMAT)
    endDate = datetime.strptime(endTime, TIME_FORMAT)
    seconds = (endDate-startDate).total_seconds()
    self.times.append(seconds)
    if self.days.get(startDate.date()):
      self.days[startDate.date()].append(seconds)
    else:
      self.days[startDate.date()] = [seconds]

  def processTime(self, line):
    separatorIndex = line.index(":")
    parts = line.split(": ")
    startOrFinish = parts[0]
    timestamp = parts[1]

    if startOrFinish == "START":
      self.processedStartTime = True
      self.startTime = timestamp
    else:
      self.processedStartTime = False
      self.logTime(self.startTime, timestamp)
      self.startTime = None

  def printOverallTimes(self):
    print "---OVERALL---"
    if len(self.times) == 0:
      print "There haven't been any builds, yet."
      print "Make sure the builds are following the correct format."
      return
    averageBuildTime = get_average(self.times)
    numDays = float(len(self.days))
    totalTimeBuilding = get_seconds_from_data(self.times)

    print "Total number of builds:    %d (over %d days)" % (len(self.times), numDays)
    print "Total time spent building: %s" % get_time_string_from_seconds(totalTimeBuilding)
    print "Average build time:        %d seconds" % averageBuildTime
    print "Average time per day:      %s" % get_time_string_from_seconds(totalTimeBuilding / numDays)
    #print "Time efficiency:           %d%%" % int(get_efficiency_percent(self.days))
    print

  def printTodayTimes(self):
    print "---TODAY---"
    todaysData = self.days.get(datetime.now().date())
    if not todaysData:
      print "There haven't been any builds today, yet."
      return
    print "Number of builds today:    %d" % len(todaysData)
    print "Time spent building today: %s" % get_time_string_from_seconds(get_seconds_from_data(todaysData))
    print "Average build time:        %d seconds" % get_average(todaysData)
    #print "Time efficiency:           %d%%" % int(get_day_efficiency_percent(self.days[datetime.now().date()]))

  def analyzeTimes(self):
    for line in self.buildTimeFile.readlines():
      line = line.strip()
      self.processTime(line) 
    self.printOverallTimes()
    self.printTodayTimes()

  def addTime(self, timeType, time):
    print "Logging time. type=%s, time=%s" % (timeType, time)


if __name__ == "__main__":
  bta = BuildTimeAnalyzer()
  print sys.argv
  if len(sys.argv) < 3:
    bta.analyzeTimes()
  else:
    bta.addTime(sys.argv[1], sys.argv[2])

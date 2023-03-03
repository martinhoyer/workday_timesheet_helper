#!/usr/bin/env python3

import argparse
from datetime import datetime, timedelta
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support import ui

DAY_START = datetime.strptime('09:00', '%H:%M')
DAYS = ['mon', 'tue', 'wed', 'thu', 'fri']


def generate_times():
    start = DAY_START
    break_start = start + timedelta(hours=3)
    break_end = break_start + timedelta(hours=1)
    end = break_end + timedelta(hours=5)
    start_str = start.strftime('%H:%M AM')
    end_str = end.strftime('%H:%M')
    break_start_str = break_start.strftime('%H:%M')
    break_end_str = break_end.strftime('%H:%M')
    return start_str, break_start_str, break_end_str, end_str


def dayint(day):
    try:
        return int(day)
    except ValueError:
        return DAYS.index(day.lower())


def main():
    parser = argparse.ArgumentParser(
        description="Workday timesheet helper"
    )

    parser.add_argument(
        "-w",
        "--week",
        dest="week",
        default=None,
        type=int,
        help="Week to fill timesheet for [number]",
    )

    parser.add_argument(
        "-s",
        "--skip",
        dest="skip",
        default=None,
        help="Comma-separated list of days to skip (Monday==0 or mon)",
    )

    parser.add_argument(
        "-m"
        "--month",
        dest="month",
        action='store_true',
    )

    args = parser.parse_args()

    now = datetime.now()
    year = now.year
    week = args.week

    if not week:
        year, week, _ = now.isocalendar()
        print("WARNING: Week not specified, using the current one")

    first_day_of_week = datetime.fromisocalendar(year, week, 1)

    if not args.month:
        print(f"Week: {week}, monday: {first_day_of_week}")

    if args.skip:
        days_to_skip = [dayint(d.strip()) for d in args.skip.split(",")]
        days_titles = ", ".join(DAYS[i].title() for i in days_to_skip)
        print(f"Days to skip: {days_titles}")
    else:
        days_to_skip = []

    br = webdriver.Firefox()
    br.implicitly_wait(2)
    wait = ui.WebDriverWait(br, 10)

    br.get('https://wd5.myworkday.com/redhat/d/home.htmld')

    sleep(1)

    wait.until(ec.element_to_be_clickable((By.XPATH, "//button[@title='Global Navigation']"))).click()
    wait.until(ec.element_to_be_clickable((By.XPATH, "//span[text()='Time']"))).click()
    wait.until(ec.element_to_be_clickable((By.XPATH, "//button[@title='Select Week']"))).click()
    day_to_send = str(first_day_of_week.month).zfill(2) + str(first_day_of_week.day).zfill(2) + str(first_day_of_week.year)
    if args.month:
        day_to_send = str(now.month).zfill(2) + str(1).zfill(2) + str(year)
    wait.until(ec.element_to_be_clickable((By.XPATH, "//input[contains(@id, 'input')]"))).send_keys(day_to_send)
    wait.until(ec.element_to_be_clickable((By.XPATH, "//span[@title='OK']"))).click()
    sleep(1)
    for i in range(5):
        print(f"Working on week {i+1}")
        if i != 0:
            wait.until(ec.element_to_be_clickable((By.XPATH, "//button[@data-automation-id='nextMonthButton']"))).click()
            sleep(1)
        wait.until(ec.element_to_be_clickable((By.XPATH, "//button[@title='Actions']"))).click()
        wait.until(ec.element_to_be_clickable((By.XPATH, "//div[@data-automation-label='Quick Add']"))).click()
        sleep(1)
        wait.until(ec.element_to_be_clickable((By.XPATH, "//button[@title='Next']"))).click()
        wait.until(ec.element_to_be_clickable((By.XPATH, "//span[@title='Add']"))).click()
        sleep(1)
        inputs = br.find_elements("xpath", "//input[@type='text']")

        times = generate_times()

        for input, time in zip(inputs[:4], times):
            input.send_keys(time)

        br.find_element("xpath", "//div[@data-automation-id='selectShowAll']").click()

        br.find_element("xpath", "//div[@title='Break']").click()

        days = br.find_elements("xpath", "//div[@data-automation-id='checkboxPanel']")

        for index, day in enumerate(days[:-2]):
            if index in days_to_skip:
                continue
            day.click()

        br.find_element("xpath", "//button[@title='Cancel']").click()
        if not args.month:
            break


if __name__ == "__main__":
    main()

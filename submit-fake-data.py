from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from faker import Faker
import openai
import time
import re
from dotenv import load_dotenv
import os
from datetime import date

load_dotenv()  # take environment variables from .env.

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Create a Faker instance
fake = Faker()

# Setup the driver. This one uses Firefox, but you can use others like Chrome
driver = webdriver.Firefox()


def extract_numbers_from_string(s):
    return ''.join(c for c in s if c.isdigit() or c == '.')

# Define a function to get the salary for a job using GPT-4


def get_salary_for_job(job_title, country):
    prompt = f"What is the average salary for a {job_title} in {country} converted to USD (do not add fluff to the response put only the number please)"
    model_response = openai.Completion.create(
        engine="text-davinci-003",  # replace with the engine you're using
        prompt=prompt,
        max_tokens=100
    )

    # Extract salary from the model's response
    salary_string = extract_numbers_from_string(
        model_response.choices[0].text.strip())
    
    salary_string = salary_string.rstrip('.')

    if salary_string:
        # If the salary string includes a decimal point, convert it to float
        # If not, convert it to integer
        salary = float(salary_string) if '.' in salary_string else int(
            salary_string)
        salary = round(salary)
        if salary >= 200000:
            # check for outliers
            salary = 0
    else:
        # In case no numeric value is found, set a default value
        salary = 0

    return salary

def calculate_age(birth_date):
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

# Define a function to fill and submit forms
def submit_form(driver):
    # Generate a fake first name
    first_name = fake.first_name()

    # Generate a fake last name
    last_name = fake.last_name()

    # Generate a fake age
    # Generate a fake age
    dob = fake.date_of_birth(minimum_age=20, maximum_age=90)
    age = calculate_age(dob)

    # Generate a fake email
    email = fake.email()

    # Generate a fake phone number
    phone_number = fake.phone_number()

    # Generate a fake job
    job = fake.job()

    # Generate a fake country
    country = fake.country()

    # Generate a salary for the job using GPT-4
    salary = get_salary_for_job(job, country)

    # Open the website
    driver.get("http://localhost:3000/")

    # Wait for the page to load completely
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "form_id")))

    # Fill the form
    time.sleep(.25)
    driver.find_element(By.ID, "first_name_input_id").send_keys(first_name)
    time.sleep(.25)
    driver.find_element(By.ID, "last_name_input_id").send_keys(last_name)
    time.sleep(.25)
    driver.find_element(By.ID, "age_input_id").send_keys(age)
    time.sleep(.25)
    driver.find_element(By.ID, "email_input_id").send_keys(email)
    time.sleep(.25)
    driver.find_element(By.ID, "phone_number_input_id").send_keys(phone_number)
    time.sleep(.25)
    driver.find_element(By.ID, "job_input_id").send_keys(job)
    time.sleep(.25)
    driver.find_element(By.ID, "country_input_id").send_keys(country)
    time.sleep(.25)
    driver.find_element(By.ID, "salary_usd_input_id").send_keys(
        salary)  # Assuming there's a salary field

    # Submit the form
    time.sleep(1)
    driver.find_element(By.ID, "submit_button_id").click()
    time.sleep(3)


# Submit a bunch of forms
for _ in range(20):
    try:
        submit_form(driver)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Pause for a while
        time.sleep(1)

# Close the driver
driver.quit()

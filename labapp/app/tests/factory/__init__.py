from faker import Faker

fake = Faker()

def generate_uid(length=14):
    return fake.sha256(raw_output=False)[:length].upper()
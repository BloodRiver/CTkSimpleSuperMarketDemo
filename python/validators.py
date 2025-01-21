def check_email_format(email: str) -> str:
    if len(email) < 5:
        raise ValueError("Email must be at least 5 characters long")

    if email.count('@') == 0:
        raise ValueError("Email must contain an @ symbol")
    
    at_index = email.index('@')
    
    if email.count('@') > 1:
        raise ValueError("Email must contain only one @ symbol")

    if email.startswith('@') or email.endswith('@'):
        raise ValueError("The @ symbol must not be at the beginning or at the end of the email.")

    if (email.count('.') == 0):
        raise ValueError("The email must contain at least one dot '.' ")

    
    if email.startswith('.') or email.endswith('.'):
        raise ValueError("The '.' symbol must not be at the beginning or at the end of the email.")
    
    if email.find('.', at_index) == -1:
        raise ValueError("A '.' symbol must appear after the @ symbol.")
    
    if email.count('\'') > 0 or email.count('\"'):
        raise ValueError("Email must not contain any '' or \"\"")
    
    return email
    
    
def check_password_format(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    if password.count('\'') > 0 or password.count('\"'):
        raise ValueError("Password must not contain any '' or \"\"")
    
    lowercase_count = 0
    uppercase_count = 0
    symbol_count = 0
    digit_count = 0
    
    for each_char in password:
        if each_char.islower():
            lowercase_count += 1
        elif each_char.isupper():
            uppercase_count += 1
        elif each_char.isdigit():
            digit_count += 1
        else:
            symbol_count += 1
 
    if lowercase_count < 1:
        raise ValueError("Password must contain at least one lowercase letter")

    if uppercase_count < 1:
        raise ValueError("Password must contain at least one uppercase letter")
    
    if symbol_count < 1:
        raise ValueError("Password must contain at least one symbol")
    
    if digit_count < 1:
        raise ValueError("Password must contain at least one number")
    
    return password
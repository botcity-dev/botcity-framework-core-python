from botcity.core import *

# Add the resource images
add_image("contact", "./resources/contact.png")
add_image("email", "./resources/email.png")
add_image("user", "./resources/user.png")
add_image("request", "./resources/request.png")

# Navigate to the website
browse("https://www.botcity.dev/")
# Wait 5 seconds so it can load
sleep(5)

# Find the email field
find("contact", confidence=0.43)

# Click relative to it
click()

# Type the email
type_text("test@botcity.dev")

# Find the username field
find("contact")

# Click relative to it
click()

# Type the username
type_text("python framework")

# Find the Request button
find("request")

# Click Request Access
#click()
from botcity.core import *

# Add the resource images
add_image("contact", "./resources/contact.png")
add_image("email", "./resources/email.png")
add_image("name", "./resources/name.png")
add_image("user", "./resources/username.png")
add_image("test", "./resources/test.png")
add_image("request", "./resources/request.png")

# Navigate to the website
browse("https://www.botcity.dev/en")
# Wait 5 seconds so it can load
sleep(5000)

# Find the contact field
find("contact", matching=0.8)
click_relative(5, 5)

# Delay for page scrolling
sleep(2)

# Find the email box
find("email")
click_relative(20, 30)

# Type the email
kb_type("test@botcity.dev")

# Find the name box
find("name")
click_relative(20, 30)
kb_type("Test Name")

# Find Software Test option
find("test")
click()

# Find the Request button
find("request")

# Move to Request Access
move()

# Click Request Access
#click()

from botcity.core import *

# Add the resource images
add_image("contact", "./resources/contact.png")
add_image("email", "./resources/email.png")
add_image("user", "./resources/user.png")
add_image("test", "./resources/test.png")
add_image("request", "./resources/request.png")

# Navigate to the website
browse("https://www.botcity.dev/")

# Wait 5 seconds so it can load
sleep(5)

# Find the contact field
find("contact")
click_relative(5, 5)

# Delay for page scrolling
sleep(2)

# Find the email box
find("email")
click_relative(20, 30)

# Type the email
type_text("test@botcity.dev")

# Find the username field
find("user")

# Click relative to it
click_relative(20, 30)

# Type the username
type_text("python framework")

# Find Software Test option
find("test")
click()

# Find the Request button
find("request")

# Click Request Access
click()

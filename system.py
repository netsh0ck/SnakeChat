import pygame
import socket  

pygame.init()

screen_width, screen_height = screen_size = (640, 640)  
font = pygame.font.Font(None, 25)
bg_color = (0.1, 0.1, 0.1)
color = (255, 255, 255)
char_width = 8
msg_spacing = 8

connection = socket.create_connection(('localhost', 1337))
connection.setblocking(False)
screen = pygame.display.set_mode(screen_size)
def msg_to_surface(msg):
    words = msg.split(' ')

    word_surfs = []
    word_locations = []
    word_x = 0
    word_y = 0
    text_height = 0

    for word in words:
        word_surf = font.render(word, True, text_color, bg_color)
        if word_x + word_surf.get_width() > screen_width:
            word_x = 0
            word_y = text_height
        word_surfs.append(word_surf)
        word_locations.append((word_x, word_y))
        word_x += word_surf.get_width() + space_character_width
        if word_y + word_surf.get_height() > text_height:
            text_height = word_y + word_surf.get_height()

    surf = pygame.Surface((screen_width, text_height))
    surf.fill(bg_color)
    for i in range(len(words)):
        surf.blit(word_surfs[i], word_locations[i])
    return surf

# New code to keep track of past msgs
msg_surfs = []

def msgAdd(msg):
    if len(msg_surfs) > 50:
        msg_surfs.pop(0)
    msg_surfs.append(msg_to_surface(msg))


text_from_socket = b''
running = True
typing_text = ""
clock = pygame.time.Clock()

def socketRead():
    global connection, text_from_socket, running
    try:
        data = connection.recv(2048)
    # Handle the error caused by non-blocking mode
    except BlockingIOError:
        return

    if not data:
        running = False
    for char in data:
        char = bytes([char])
        if char == b'\n':
            add_msg(text_from_socket.strip().decode('utf-8'))  
            text_from_socket = b''
        else:
            text_from_socket += char


def redraw_screen():
    screen.fill(bg_color)

    typing_surf = msg_to_surface("> " + typing_text)
    y = screen_height - typing_surf.get_height()
    screen.blit(typing_surf, (0, y))

    msg_index = len(msg_surfs) - 1
    while y > 0 and msg_index >= 0:
        msg_surf = msg_surfs[msg_index]
        msg_index -= 1
        y -= msg_surf.get_height() + msg_spacing
        screen.blit(msg_surf, (0, y))
    pygame.display.flip()



while 1:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if typing_text:
                    typing_text = typing_text[:-1]
            elif event.key == pygame.K_RETURN:
               
                add_msg('Your User: ' + typing_text)
                connection.send("\n")
                type_text = "."
            else:
                type_text += event.unicode

    
    read_from_socket()
    redraw_screen()

pygame.quit()
connection.close()  # Close the connection when we're done

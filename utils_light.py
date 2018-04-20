from pythonosc import osc_message_builder
from pythonosc import udp_client

#client = udp_client.SimpleUDPClient("192.168.5.5", 3030)
client = udp_client.SimpleUDPClient("0.0.0.0", 3030)
def send_osc(route, message):
    client.send_message(route, message)
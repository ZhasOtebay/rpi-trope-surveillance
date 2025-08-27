#!/bin/bash

# Удаляем default route через Ethernet (если есть)
sudo ip route del default via 192.168.1.1 dev eth0 2>/dev/null || true

# Устанавливаем default route через Wi-Fi
WLAN_GATEWAY=$(ip route show | grep "default via" | grep wlan0 | awk '{print $3}')
if [ -z "$WLAN_GATEWAY" ]; then
    # Если нет default route, добавляем через wlan0
    sudo ip route add default via 192.168.43.1 dev wlan0
fi

# Добавляем маршрут для камеры через Ethernet
sudo ip route add 192.168.1.100 via 192.168.1.1 dev eth0

# Добавляем маршрут для AWS сервера через Wi-Fi
sudo ip route add 100.26.111.7 via 192.168.43.1 dev wlan0

# Проверяем маршрутизацию
echo "=== Current Routing Table ==="
ip route show

echo "=== Testing Camera Connection ==="
ping -c 2 -I eth0 192.168.1.100

echo "=== Testing AWS Connection ==="
ping -c 2 -I wlan0 100.26.111.7

echo "=== Testing Internet ==="
ping -c 2 -I wlan0 8.8.8.8

# -*- coding: utf-8 -*-
#안드로이드 -> 서버(python)에 소켓통신으로 사진 전송하는것

from socket import *
import socket
import os
import time
import sys

src = './image'

#파일이름 생성하는 함수 fileName
def fileName():
    dte = time.localtime()
    Year = dte.tm_year
    Mon = dte.tm_mon
    Day = dte.tm_mday
    WDay = dte.tm_wday
    Hour = dte.tm_hour
    Min = dte.tm_min
    Sec = dte.tm_sec
    imgFileName = str(Year) + '_' + str(Mon) + '_' + str(Day) + '_' + str(Hour) + '_' + str(Min) + '_' + str(Sec) + '.jpg'
    return imgFileName

def main2():
    # 서버 소켓 오픈 (bind 함수의 아이피와 포트번호 변경)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # 소켓 객체를 생성(인자 : 패밀리 - 주소체계 종류, 타입 - 소켓타입), 지금 인지는 default
    server_socket.bind(("10.10.13.81", 8809))						# 서버가 소켓을 포트에 맵핑하는 행위 - 바인딩, (호스트이름, 포트번호)튜블로 인자 보냄
    server_socket.listen(3)												# 클라이언트가 바인드된 포트로 연결할때까지 기다리는 블록킹 함수

    print("TCPServer Waiting for client on port")

    while True:
        # 클라이언트 요청 대기중 .
        client_socket, address = server_socket.accept()					# 해당 클라이언트 연결을 받아들이기위한 accept함수
        # 연결 요청 성공
        print("I got a connection from ", address)						# 연결된 클라이언트의 주소 address를 출력시킴

        data = None

        # Data 수신
        while True:
            img_data = client_socket.recv(1024)  #client대기 기다림			# 연결된 클라이언트 소켓(안드로이드)으로부터 데이터를 읽을때 사용하는 함수
            data = img_data
            if img_data:
                while img_data:
                    img_data = client_socket.recv(1024)
                    data += img_data
                else:
                    break

            # 파일 이름 생성해서 변수에 저장해서 출력
        img_fileName = fileName()
        print(img_fileName)

        # 받은 이미지 폴더에 저장
        img_file = open(img_fileName, "wb")

        # 파일 크기
        print(sys.getsizeof(data))
        print("Finish ")

        img_file.write(data)
        img_file.close()
        client_socket.close()		# 클라이언트 소켓 닫아줌
        print("SOCKET closed... END")

        return img_fileName
        

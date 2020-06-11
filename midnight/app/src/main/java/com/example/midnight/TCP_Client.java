package com.example.midnight;

import android.os.AsyncTask;
import android.util.Log;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;

public class TCP_Client extends AsyncTask<String, String, String> {
	//아이피와 포트번호 변경할것
    protected static String SERV_IP = "192.168.219.188";
    protected static int PORT = 8809;

    @Override
    protected String doInBackground(String... imagePath) {
        try {
            //Log.d("PATH", "imagePath : " + imagePath[0]);
            Log.d("TCP", "server connecting");
            InetAddress serverAddr = InetAddress.getByName(SERV_IP);
            Socket sock = new Socket(serverAddr, PORT);         // 클라이언트 소켓 생성

            try{
                Log.d("State", "데이터 찾는 중");

                File file = new File(imagePath[0]);

                // 소켓의 입력과 출력스트림 선언(for 양방향 통신)
                DataInputStream dis = new DataInputStream(new FileInputStream(file));
                DataOutputStream dos = new DataOutputStream(sock.getOutputStream());             // 소켓의 출력스트림을 얻어, 기본형 단위로 처리하는 보조 스트링 dos생성


                long fileSize = file.length();
                byte[] buf = new byte[1024];

                long totalReadBytes = 0;
                int readBytes;
                Log.d("State", "데이터 찾기 끝");

                /* 서버로 보내기 위해서 보낼 데이터 길이 알아내는 작업 */
                // dis의 데이터를 buf로 읽어들임, readBytes는 얼마나 읽어들인 크키를 저장?
                while ((readBytes = dis.read(buf)) > 0){  // 읽어들인 bytes를 저장
                    //Log.d("State", "while");
                    dos.write(buf, 0, readBytes);    // buf를 dos로 쓰기
                    totalReadBytes += readBytes;         // 읽어들인 bytes를 더함
                }

                //Log.d("State", "데이터 보내기 끝 직전");
                dos.close();
                Log.d("State", "데이터 끝");
            } catch(IOException e){
                Log.d("TCP", "dont send message");
            }
        } catch (UnknownHostException e){
            e.printStackTrace();
        } catch (IOException e){
            e.printStackTrace();
        }
        return null;
    }
}


package com.example.midnight;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Message;
import android.os.StrictMode;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class MenuActivity extends AppCompatActivity {

    Button btn;
    TextView tv;

    TCP_Client tc;

    String data;

    private int port = 53535;
    private final String ip = "192.168.219.188";

    //  TCP연결 관련
    private Socket clientSocket;
    private BufferedReader socketIn;
    private PrintWriter socketOut;

    private MyHandler1 myHandler1;
    private MyThread1 myThread1;

    String mCurrentPhotoPath;

    private static final int INTENT_REQUEST_CODE = 100;
    private static final int INTENT_REQUEST_CODE_CAMERA = 105;
    private static final int MULTIPLE_PERMISSIONS = 101;

    private String[] permissions = {
            Manifest.permission.READ_EXTERNAL_STORAGE,          // 기기, 사진, 미디어, 파일 엑세스 권한
            Manifest.permission.CAMERA
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_menu);

        Button btn1 = (Button) findViewById(R.id.Button01);
        Button cameraBtn = (Button) findViewById(R.id.Button02);

        if (Build.VERSION.SDK_INT > 22) {
            checkPermissions();
        }

        btn1.setOnClickListener(view -> {
            StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
            StrictMode.setThreadPolicy(policy);

            try {
                clientSocket = new Socket(ip, port);
                Log.w("@@@", "서버 접속됨");
                socketIn = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
                socketOut = new PrintWriter(clientSocket.getOutputStream(), true);
            } catch (Exception e) {
                Log.w("@@@", "서버접속못함");
                e.printStackTrace();
            }
            Intent intent = new Intent(Intent.ACTION_PICK);
            intent.setType("image/*");
            startActivityForResult(intent, INTENT_REQUEST_CODE);
        });

        cameraBtn.setOnClickListener(view -> {
            Intent main1 = new Intent(this, MainActivity.class);
            //myThread1.interrupt();
            startActivity(main1);
            /*
            Intent takePictureIntent = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE);
            // Ensure that there's a camera activity to handle the intent
            File photoFile = null;
            try {
                photoFile = createImageFile();
            } catch (IOException ex) {
                // Error occurred while creating the File
            }
            // Continue only if the File was successfully created

            if (photoFile != null) {
                Log.d("@@@", "도착1");
                Uri photoURI = FileProvider.getUriForFile(this,
                        "com.example.midnight.fileprovider",
                        photoFile);
                Log.d("@@@", "도착 : " + photoURI);
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
                startActivityForResult(takePictureIntent, INTENT_REQUEST_CODE_CAMERA);
            }
             */
        });

        btn = (Button) findViewById(R.id.btn);
        tv = (TextView) findViewById(R.id.tv);
        btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                socketOut.println(456);
            }
        });
    }

    public void onClick(View view){
        // 서브 액티비티 생성하기 위한 intent3생성
        Intent sub = new Intent(this, SubActivity.class);
        // 웹뷰를 위해서 서브액티비티로 전달
        sub.putExtra("value", data);
        startActivity(sub);
    }

    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == INTENT_REQUEST_CODE) {
            if (resultCode == RESULT_OK) {
                Log.d("@@@", "접속");
                Uri imgUri = data.getData();
                String imagePath = getRealPathFromURI(imgUri);
                imgUri = null;
                //Log.d("@@@", "imgUri : " + imgUri);
                Log.d("@@@", "imagePath : " + imagePath);

                socketOut.println(456);

                myHandler1 = new MyHandler1();
                myThread1 = new MyThread1();
                myThread1.start();

                tc = new TCP_Client();
                tc.execute(imagePath);
                imagePath = null;
            }
        } else if (requestCode == INTENT_REQUEST_CODE_CAMERA) {
            //Uri currImageURI = data.getData();
            //Log.d("@@@", "CAMERA URI : " + currImageURI);mCurrentPhotoPath
            tc = new TCP_Client();
            tc.execute(mCurrentPhotoPath);
        }
    }

    public String getRealPathFromURI(Uri contentUri) {
        String[] proj = {MediaStore.Images.Media.DATA};
        Cursor cursor = getContentResolver().query(contentUri, proj, null, null, null);
        cursor.moveToFirst();
        int column_index = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA);

        return cursor.getString(column_index);
    }

    class MyThread1 extends Thread {
        @Override
        public void run() {
            while (true) {
                try {
                    sleep(1500);
                    // InputStream의 값을 읽어와서 data에 저장
                    data = socketIn.readLine();
                    // Message 객체를 생성, 핸들러에 정보를 보낼 땐 이 메세지 객체를 이용
                    Message msg = myHandler1.obtainMessage();
                    Log.d("@@@", "abcd : " + msg);
                    msg.obj = data;
                    myHandler1.sendMessage(msg);

                    /*
                    if (msg != null){
                        msg = null;
                        break;
                    }
                    */
                }
                catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    }

    class MyHandler1 extends Handler {
        @Override
        public void handleMessage(Message msg) {
            tv.setText(msg.obj.toString());
            String a = msg.obj.toString();
            data = null;
            msg = null;
            Intent sub1 = new Intent(getApplicationContext(), SubActivity.class);
            // 웹뷰를 위해서 서브액티비티로 전달
            sub1.putExtra("value", a);
            startActivity(sub1);
        }
    }

    private boolean checkPermissions() {
        int result;
        List<String> permissionList = new ArrayList<>();
        for (String pm : permissions) {
            result = ContextCompat.checkSelfPermission(this, pm);
            if (result != PackageManager.PERMISSION_GRANTED) {
                permissionList.add(pm);
            }
        }
        if (!permissionList.isEmpty()) {
            ActivityCompat.requestPermissions(this, permissionList.toArray(new String[permissionList.size()]), MULTIPLE_PERMISSIONS);
            return false;
        }
        return true;
    }

    private File createImageFile() throws IOException {
        // Create an image file name
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        File image = File.createTempFile(
                imageFileName,  /* prefix */
                ".jpg",         /* suffix */
                storageDir      /* directory */
        );

        // Save a file: path for use with ACTION_VIEW intents
        mCurrentPhotoPath = image.getAbsolutePath();
        Log.d("@@@", "알수없는 : " + mCurrentPhotoPath);
        return image;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        switch (requestCode) {
            case MULTIPLE_PERMISSIONS: {
                if (grantResults.length > 0) {
                    for (int i = 0; i < permissions.length; i++) {
                        if (permissions[i].equals(this.permissions[i])) {
                            if (grantResults[i] != PackageManager.PERMISSION_GRANTED) {
                                showToast_PermissionDeny();
                            }
                        }
                    }
                } else {
                    showToast_PermissionDeny();
                }
                return;
            }
        }

    }
    private void showToast_PermissionDeny() {
        Toast.makeText(this, "권한 요청에 동의 해주셔야 이용 가능합니다. 설정에서 권한 허용 하시기 바랍니다.", Toast.LENGTH_SHORT).show();
        finish();
    }

}

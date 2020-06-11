package com.example.midnight;

import android.content.Intent;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.appcompat.app.AppCompatActivity;

public class SubActivity extends AppCompatActivity {

    private WebView mWebView;
    private WebSettings mWebSettings;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sub);

        // 수식 데이터 받아옴
        Intent intent = getIntent();
        String tempMath = intent.getStringExtra("value");

        // 웹뷰세팅
        mWebView = (WebView)findViewById(R.id.webview);
        mWebView.setWebViewClient(new WebViewClient());
        mWebSettings = mWebView.getSettings();
        mWebSettings.setJavaScriptEnabled(true);

        // 수식 데이터 url에 맞게 변형
        int i;
        for(i=0;i<tempMath.length();i++){

            //if(math.charAt(i)>='0' && math.charAt(i)<='9') url<<eqn[i];
            //  if(eqn[i]=='-')url<<eqn[i];
            //  if(eqn[i]=='f')url<<eqn[i];
            // if(eqn[i]=='x')url<<eqn[i];

            if(tempMath.charAt(i) =='+') tempMath = tempMath.replace("+", "%2B");
            if(tempMath.charAt(i) =='=') tempMath = tempMath.replace("=", "%3D");
            if(tempMath.charAt(i) =='^') tempMath = tempMath.replace("*", "%5e");
            if(tempMath.charAt(i) =='/') tempMath = tempMath.replace("*", "%2f");
            if(tempMath.charAt(i) =='\\') tempMath = tempMath.replace("\\", "%5c");
            if(tempMath.charAt(i) =='{') tempMath = tempMath.replace("{", "%7b");
            if(tempMath.charAt(i) =='}') tempMath = tempMath.replace("}", "%7d");
            if(tempMath.charAt(i) =='[') tempMath = tempMath.replace("[", "%5b");
            if(tempMath.charAt(i) ==']') tempMath = tempMath.replace("]", "%5d");



            /*if(eqn[i]=='^')url<<"%5E";
            if(eqn[i]=='=')url<<"%3D";
            if(eqn[i]=='(')url<<"%28";
            if(eqn[i]==')')url<<"%29";
*/

        }

        String url = "https://www.wolframalpha.com/input/?i=" + tempMath;

        mWebView.loadUrl(url);

    }
}

server {
    listen 8000;

    server_name app.muteshi.com;
    server_tokens off;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
location / {
        return 301 https://app.muteshi.com$request_uri;
    }
     

}

server {
    listen 443 ssl;

    server_name app.muteshi.com;
    server_tokens off;
    
    client_max_body_size     10M;

    ssl_certificate /etc/nginx/ssl/live/app.muteshi.com/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/live/app.muteshi.com/privkey.pem;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location /admin {
       uwsgi_pass               ${APP_HOST}:${APP_PORT};
       include                 /etc/nginx/uwsgi_params;
       
    }

    location /api {
       uwsgi_pass               ${APP_HOST}:${APP_PORT};
       include                 /etc/nginx/uwsgi_params;
       
    }

    location /static {
        alias /vol/static;
    }

     

}


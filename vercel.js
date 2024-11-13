{
  "builds": [
    {
      "src": "/inmueblebi/wsgi.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "15mb" }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "inmueblebi/wsgi.py"
    },
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    }
  ]
}

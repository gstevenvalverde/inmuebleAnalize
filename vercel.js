{
  "version": 2,
  "builds": [
    {
      "src": "inmueblebi/wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/staticfiles/$1"
    },
    {
      "src": "/(.*)",
      "dest": "inmueblebi/wsgi.py"
    }
  ]
}

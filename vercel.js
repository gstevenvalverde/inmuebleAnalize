{
    "builds" : [
        {
            "src": "inmueblebi/wsgi.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "inmueblebi/wsgi.py"
        }
    ]
}
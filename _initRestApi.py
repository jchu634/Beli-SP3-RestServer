from fastapi import FastAPI


def create_app(aargs=None):
    
    tags_metadata = [
        {
            "name": "plugs",
            "description": "API routes which communicate to the plugs."
        },
        {
            "name": "Home",
            "description": "Api dedicated to serving the React App for local app client+server deployment."
        },
    ]
    app = FastAPI(openapi_tags=tags_metadata)
    
    # app.add_middleware(
    #     allow_origins=["*"],
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    # )

    from library.plug import plugComs
    app.include_router(plugComs.plug_router)

    return app

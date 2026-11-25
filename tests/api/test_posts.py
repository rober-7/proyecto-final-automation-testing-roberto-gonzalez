"""Tests de API del recurso /posts de JSONPlaceholder (GET, POST y DELETE).

Cada test valida el codigo de estado HTTP, la estructura del JSON
(campos y tipos) y el contenido de la respuesta.
"""

import pytest

from utils.api_client import assert_estructura
from utils.data_reader import read_json

API_DATA = read_json("api.json")

ESQUEMA_POST = {"userId": int, "id": int, "title": str, "body": str}


class TestPosts:
    def test_listar_posts_devuelve_todos_con_estructura_valida(self, api_client, api_data):
        respuesta = api_client.get("/posts")

        assert respuesta.status_code == 200
        assert "application/json" in respuesta.headers["Content-Type"]

        posts = respuesta.json()
        assert isinstance(posts, list)
        assert len(posts) == api_data["total_posts"]
        for post in posts:
            assert_estructura(post, ESQUEMA_POST)

    @pytest.mark.parametrize("post_id", API_DATA["posts_existentes"])
    def test_obtener_post_por_id(self, api_client, post_id):
        respuesta = api_client.get(f"/posts/{post_id}")

        assert respuesta.status_code == 200
        post = respuesta.json()
        assert_estructura(post, ESQUEMA_POST)
        assert post["id"] == post_id
        assert post["title"].strip() != ""

    def test_obtener_post_inexistente_devuelve_404(self, api_client, api_data):
        respuesta = api_client.get(f"/posts/{api_data['post_inexistente']}")

        assert respuesta.status_code == 404
        assert respuesta.json() == {}

    def test_crear_post_devuelve_201_con_los_datos_enviados(self, api_client, api_data):
        nuevo_post = api_data["nuevo_post"]

        respuesta = api_client.post("/posts", json=nuevo_post)

        assert respuesta.status_code == 201
        post_creado = respuesta.json()
        assert_estructura(post_creado, ESQUEMA_POST)
        assert post_creado["id"] == api_data["id_asignado_a_post_nuevo"]
        for campo, valor in nuevo_post.items():
            assert post_creado[campo] == valor

    def test_eliminar_post_devuelve_200_y_cuerpo_vacio(self, api_client):
        respuesta = api_client.delete("/posts/1")

        assert respuesta.status_code == 200
        assert respuesta.json() == {}

"""Tests de API con peticiones encadenadas: cada peticion usa datos de la anterior.

JSONPlaceholder no guarda los recursos creados con POST, por eso los flujos
encadenan lecturas de recursos relacionados (usuario -> posts -> comentarios).
"""

from utils.api_client import assert_estructura

ESQUEMA_USUARIO = {
    "id": int, "name": str, "username": str, "email": str,
    "address": dict, "phone": str, "website": str, "company": dict,
}
ESQUEMA_COMENTARIO = {"postId": int, "id": int, "name": str, "email": str, "body": str}


class TestFlujosEncadenados:
    def test_obtener_usuario_y_luego_sus_posts(self, api_client, api_data):
        # 1) Se obtiene el usuario
        respuesta_usuario = api_client.get(f"/users/{api_data['usuario_para_flujo']}")
        assert respuesta_usuario.status_code == 200
        usuario = respuesta_usuario.json()
        assert_estructura(usuario, ESQUEMA_USUARIO)

        # 2) Con el id recibido se piden sus posts
        respuesta_posts = api_client.get("/posts", params={"userId": usuario["id"]})
        assert respuesta_posts.status_code == 200
        posts = respuesta_posts.json()

        assert len(posts) > 0
        assert all(post["userId"] == usuario["id"] for post in posts)

    def test_obtener_primer_post_del_usuario_y_luego_sus_comentarios(self, api_client, api_data):
        # 1) Se obtienen los posts del usuario y se toma el primero
        posts = api_client.get("/posts", params={"userId": api_data["usuario_para_flujo"]}).json()
        primer_post_id = posts[0]["id"]

        # 2) Con el id de ese post se piden sus comentarios
        respuesta = api_client.get(f"/posts/{primer_post_id}/comments")
        assert respuesta.status_code == 200
        comentarios = respuesta.json()

        assert len(comentarios) > 0
        for comentario in comentarios:
            assert_estructura(comentario, ESQUEMA_COMENTARIO)
            assert comentario["postId"] == primer_post_id
            assert "@" in comentario["email"]

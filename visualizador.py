

import base64
import os
import sys
import threading
import time

import webview


class Api:
    def __init__(self):
        self.pasta_atual = None
        self.estado_arquivos = {}
        self.monitorando = True
        self.offset = 0
        self.limite = 10

    def selecionar_pasta(self, limite=10):
        try:
            window = webview.windows[0]
            dialog_type = getattr(webview, 'FileDialog', None)
            modo = dialog_type.FOLDER if dialog_type else webview.FOLDER_DIALOG

            resultado = window.create_file_dialog(modo)
            if not resultado:
                return None

            self.pasta_atual = resultado[0]
            self.offset = 0
            self.limite = max(1, int(limite))
            self.estado_arquivos = self._obter_assinatura_pasta(self.pasta_atual)
            return self.carregar_imagens()
        except Exception as e:
            return {"erro": f"Falha ao abrir diálogo: {str(e)}"}

    def atualizar_manual(self):
        if not self.pasta_atual:
            return None
        self.estado_arquivos = self._obter_assinatura_pasta(self.pasta_atual)
        return self.carregar_imagens()

    def alterar_limite(self, novo_limite):
        try:
            valor = int(novo_limite)
            self.limite = max(1, valor)
        except (ValueError, TypeError):
            self.limite = 10

        self.offset = 0
        if not self.pasta_atual:
            return None
        return self.carregar_imagens()

    def avancar_lote(self):
        if not self.pasta_atual:
            return None

        arquivos = self._listar_arquivos_ordenados()
        total = len(arquivos)

        if total == 0:
            self.offset = 0
        elif self.offset + self.limite >= total:
            self.offset = 0
        else:
            self.offset += self.limite

        return self.carregar_imagens()

    def voltar_lote(self):
        if not self.pasta_atual:
            return None

        arquivos = self._listar_arquivos_ordenados()
        total = len(arquivos)

        if total == 0:
            self.offset = 0
        elif self.offset - self.limite < 0:
            # Vai para o início do último lote disponível
            ultimo_offset = ((total - 1) // self.limite) * self.limite
            self.offset = ultimo_offset
        else:
            self.offset -= self.limite

        return self.carregar_imagens()

    def _listar_arquivos_ordenados(self):
        extensoes_validas = ('.png', '.jpg', '.jpeg')
        return sorted([
            f for f in os.listdir(self.pasta_atual)
            if f.lower().endswith(extensoes_validas)
            and os.path.isfile(os.path.join(self.pasta_atual, f))
        ])

    def _obter_assinatura_pasta(self, pasta):
        extensoes = ('.png', '.jpg', '.jpeg')
        assinatura = {}
        try:
            for f in os.listdir(pasta):
                caminho = os.path.join(pasta, f)
                if f.lower().endswith(extensoes) and os.path.isfile(caminho):
                    assinatura[f] = os.path.getmtime(caminho)
        except Exception:
            pass
        return assinatura

    def carregar_imagens(self):
        if not self.pasta_atual:
            return None

        try:
            todos_arquivos = self._listar_arquivos_ordenados()
        except Exception as e:
            return {"erro": str(e)}

        total = len(todos_arquivos)

        if self.offset >= total:
            self.offset = 0

        arquivos_lote = todos_arquivos[self.offset:self.offset + self.limite]

        imagens = []
        for nome in arquivos_lote:
            caminho_completo = os.path.join(self.pasta_atual, nome)
            ext = os.path.splitext(nome)[1].lower().replace('.', '')
            if ext == 'jpg':
                ext = 'jpeg'

            try:
                with open(caminho_completo, "rb") as img_file:
                    b64_data = base64.b64encode(img_file.read()).decode('utf-8')
                    imagens.append({
                        "nome": nome,
                        "src": f"data:image/{ext};base64,{b64_data}"
                    })
            except Exception:
                continue

        return {
            "pasta": self.pasta_atual,
            "imagens": imagens,
            "total": total,
            "inicio": self.offset + 1 if total > 0 else 0,
            "fim": min(self.offset + len(imagens), total)
        }

    def iniciar_monitoramento(self, window):
        def loop():
            while self.monitorando:
                time.sleep(1.0)
                if self.pasta_atual:
                    novo_estado = self._obter_assinatura_pasta(self.pasta_atual)
                    if novo_estado != self.estado_arquivos:
                        self.estado_arquivos = novo_estado
                        time.sleep(0.15)
                        window.evaluate_js("recarregarAutomaticamente()")

        t = threading.Thread(target=loop, daemon=True)
        t.start()

def obter_caminho_recurso(nome_arquivo):
    """Retorna o caminho absoluto do recurso, funcionando tanto em dev quanto no .exe do PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, nome_arquivo)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_arquivo)

if __name__ == '__main__':
    api = Api()
    caminho_html = obter_caminho_recurso('interface.html')

    window = webview.create_window(
        title='Visualizador de Fases de Transformação',
        url=caminho_html,
        js_api=api,
        width=1360,
        height=860,
        resizable=True
    )
    webview.start(api.iniciar_monitoramento, window)
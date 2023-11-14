# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pdf_to_pptx.py'],
    pathex=[],
    binaries=[('lib', 'lib')],
    datas=[('template', 'template'), ('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='pdf_to_pptx',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/app.ico'],
)
app = BUNDLE(
    exe,
    name='pdf_to_pptx.app',
    icon='assets/app.ico',
    bundle_identifier=None,
)

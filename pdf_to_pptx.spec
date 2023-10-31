# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pdf_to_pptx.py'],
    pathex=[],
    binaries=[],
    datas=[('lib/poppler', 'lib/poppler'), ('template', 'template'), ('lib/tkinterdnd2', 'tkinterdnd2')],
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
)

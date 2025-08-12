# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['box_game_app_optimized.py'],
    pathex=[],
    binaries=[],
    datas=[('interfaces', 'interfaces'), ('utils', 'utils'), ('data_processing', 'data_processing'), ('backends', 'backends'), ('config', 'config'), ('extern', 'extern'), ('multiple_skins', 'multiple_skins'), ('server', 'server'), ('with_nn', 'with_nn'), ('config.json', '.')],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'PyQt5.sip', 'numpy', 'scipy', 'matplotlib', 'cv2', 'PIL', 'pandas', 'sklearn', 'seaborn', 'yaml', 'openpyxl', 'loguru', 'colorama', 'psutil', 'scipy.ndimage', 'scipy.signal', 'scipy.optimize', 'matplotlib.pyplot', 'matplotlib.backends.backend_qt5agg', 'PIL.Image', 'skimage', 'sklearn.ensemble', 'sklearn.cluster', 'sklearn.decomposition', 'sklearn.preprocessing', 'sklearn.metrics', 'sklearn.model_selection', 'sklearn.neighbors', 'sklearn.svm', 'sklearn.tree', 'sklearn.linear_model', 'sklearn.naive_bayes', 'sklearn.neural_network', 'sklearn.feature_extraction', 'sklearn.feature_selection', 'sklearn.pipeline', 'sklearn.cross_decomposition', 'sklearn.covariance', 'sklearn.manifold', 'sklearn.mixture', 'sklearn.semi_supervised', 'sklearn.calibration', 'sklearn.multioutput', 'sklearn.compose', 'sklearn.impute', 'sklearn.kernel_ridge', 'sklearn.discriminant_analysis', 'sklearn.gaussian_process', 'sklearn.isotonic', 'sklearn.kernel_approximation', 'sklearn.metrics.cluster', 'sklearn.metrics.pairwise', 'sklearn.metrics.ranking', 'sklearn.metrics.regression', 'sklearn.metrics.scorer', 'sklearn.metrics._classification', 'sklearn.metrics._regression', 'sklearn.metrics._ranking', 'sklearn.metrics._scorer', 'sklearn.metrics._dist_metrics', 'sklearn.metrics._pairwise_distances_reduction', 'sklearn.metrics._pairwise_fast', 'sklearn.metrics._pairwise'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6', 'PySide2', 'PySide6'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='推箱子游戏',
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

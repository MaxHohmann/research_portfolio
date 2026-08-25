"""
SWIFT (Semantic Wavelet-Induced Frequency Tagging) – Python implementation

This function generates a cyclic sequence of images by modulating the semantic
information of an input image at a target temporal frequency (f0). The modulation
is achieved by rotating wavelet detail coefficients along circular trajectories
in coefficient space, while preserving local energy. The resulting image sequence 
preserves low-level visual properties (luminance, contrast, spatial frequency 
content) while periodically disrupting semantic structure.

INPUT:      
            f0 : float
                target temporal frequency (Hz) of semantic modulation.
            frame_rate : float
                presentation frame rate (frames per second).
            in_img : ndarray
                input image, either 2D (grayscale) or 3D (RGB).

OUTPUT:
            sequence : ndarray
                3D array of shape (nb_frames, height, width) containing one full SWIFT cycle.
                The first frame corresponds to the original (unscrambled) image.

References:
Koenig-Robert, R., VanRullen, R. (2013).
SWIFT: A novel method to track the neural correlates of recognition, 
NeuroImage, http://dx.doi.org/10.1016/j.neuroimage.2013.04.116

Version:    1.1
Date:       27/04/2026  
Author:     Maximilian Hohmann
            maximilian.hohmann@stud.uni-goettingen.de
"""


import numpy as np
import pywt
import warnings
from scipy.stats import rv_discrete


# -------------------------
# SWIFT main function
# -------------------------
def swift(f0, frame_rate, in_img):

    # ----- parameters -----
    np.random.seed(42)      # seed for reproducibility
    freqdist = [0.2] * 5    # probability distribution over harmonics
    levels   = 8            # number of wavelet decomposition levels
    wavelet  = 'dmey'       # wavelet filter
    scale_factor = 2        # scale radius of circular trajectories


    # frames per cycle
    nbframes = frame_rate / f0

    # ensure integer number of frames
    if nbframes % 1 != 0:
        nbframes = int(round(nbframes))
        f0 = frame_rate / nbframes
        print(f"f0 changed to {f0:.3f} Hz")

    nbframes = int(nbframes)
    harms = np.arange(1, len(freqdist) + 1)


    # initialize sequence
    in_img = in_img.astype(np.float64)

    H, W = in_img.shape
    sequence = np.zeros((nbframes, H, W), dtype=np.float64)


    # ----- wavelet decomposition -----
    warnings.filterwarnings("ignore", category=UserWarning, module="pywt")  # disable pywt warnings

    coeffs  = pywt.wavedec2(in_img, wavelet, level=levels)
    app     = coeffs[0]         # approximation coefficients
    details = coeffs[1:]        # detail coefficients per level (H, V, D)

    warnings.filterwarnings("default", category=UserWarning, module="pywt") # re-enable pywt warnings
    

    # ----- random vectors -----
    # two random coefficient triplets for each wavelet level
    h1 = []; v1 = []; d1 = []
    h2 = []; v2 = []; d2 = []

    for h, v, d in details:

        # local energy 
        energy = np.sqrt(h*h + v*v + d*d)

        # random vectors in coefficient space
        r1 = 2*np.random.rand(*h.shape, 3) - 1
        r2 = 2*np.random.rand(*h.shape, 3) - 1

        # multiply random vectors
        r1 *= scale_factor
        r2 *= scale_factor

        # normalize random vectors
        n1 = np.linalg.norm(r1, axis=2)
        n2 = np.linalg.norm(r2, axis=2)
        n1[n1 == 0] = 1
        n2[n2 == 0] = 1

        # scale random vectors to preserve local energy
        h1.append(energy * r1[:,:,0] / n1)
        v1.append(energy * r1[:,:,1] / n1)
        d1.append(energy * r1[:,:,2] / n1)

        h2.append(energy * r2[:,:,0] / n2)
        v2.append(energy * r2[:,:,1] / n2)
        d2.append(energy * r2[:,:,2] / n2)


    # ----- circular trajectories -----
    circle = [[None]*levels for _ in range(nbframes)]   # preallocate

    for lvl in range(levels):

        h, v, d = details[lvl]

        # circle defined by coefficient points
        p1 = np.stack([h, v, d], axis=2)        # original
        p2 = np.stack([h1[lvl], v1[lvl], d1[lvl]], axis=2)
        p3 = np.stack([h2[lvl], v2[lvl], d2[lvl]], axis=2)

        # compute circle center and radius
        t = p2 - p1
        u = p3 - p1
        v_ = p3 - p2
        w = np.cross(t, u)

        dottt = np.sum(t*t, axis=2)
        dotuu = np.sum(u*u, axis=2)
        dotvv = np.sum(v_*v_, axis=2)
        dottv = np.sum(t*v_, axis=2)
        dotuv = np.sum(u*v_, axis=2)
        dotww = np.sum(w*w, axis=2)
        dotww[dotww == 0] = 1

        c = p1 + (
            dottt[...,None]*dotuv[...,None]*u -
            dotuu[...,None]*dottv[...,None]*t
        ) / (2*dotww[...,None])

        r = 0.5*np.sqrt(dottt*dotuu*dotvv/dotww)

        x1 = p1 - c
        x2 = p2 - c
        x3 = p3 - c

        den = np.sum(x1*x2, axis=2)
        den[den == 0] = 1
        alpha = -np.sum(x1*x3, axis=2) / den

        pprime = c + x3 + alpha[...,None]*x2
        normp = np.linalg.norm(pprime-c, axis=2)
        normp[normp == 0] = 1

        xprime = r[...,None]*(pprime-c)/normp[...,None]

        # random harmonic assignment per pixel
        rng = rv_discrete(values=(harms, freqdist))
        freq = rng.rvs(size=h.shape)

        # random phase jitter for each level
        phase0 = 2 * np.pi * np.random.rand(*h.shape)

        # generate frames along circular trajectory
        for frame in range(nbframes):
            if frame == 0:
                circle[frame][lvl] = p1  # original
            else:
                # compute angle
                angle = 2 * np.pi * freq * frame / nbframes + phase0
                dtheta = angle - phase0

                # cos and sin along circular trajectory
                cosw = np.cos(dtheta)[..., None]
                sinw = np.sin(dtheta)[..., None]
                circle[frame][lvl] = c + cosw*x1 + sinw*xprime


    # ----- frame reconstruction from wavelet coefficients -----
    for frame in range(nbframes):

        frame_coeffs = [app]

        for lvl in range(levels):

            coord = circle[frame][lvl]

            frame_coeffs.append((
                coord[:,:,0],
                coord[:,:,1],
                coord[:,:,2]
                ))
            
        sequence[frame] = pywt.waverec2(frame_coeffs, wavelet)


    # ----- temporal FFT normalization -----
    # frequency axis
    fpixel = np.linspace(0, frame_rate, nbframes)

    # highest and penultimate harmonics
    last = f0 * harms[-1]
    prev = f0 * harms[-2]

    # cutoff frequency bin
    c1 = np.argmin(np.abs(fpixel - prev))
    c2 = np.argmin(np.abs(fpixel - last))
    cutoff = c2 + round((c2 - c1)/2)

    # FFT along time axis
    Y = np.fft.fft(sequence, axis=0)
    Ynorm = Y.copy()

    # global target amplitude 
    target_amp = 0.8 * np.mean(np.abs(Y[1:cutoff]), axis=(0,1,2))

    # normalize allowed frequency band
    Ynorm[1:cutoff] = (target_amp * Y[1:cutoff] /
                    np.maximum(np.abs(Y[1:cutoff]), 1e-12))

    # remove higher frequencies
    Ynorm[cutoff:nbframes-cutoff+1] = 0

    # keep DC unchanged
    Ynorm[0] = Y[0]

    # inverse FFT
    sequence = np.real(np.fft.ifft(Ynorm, axis=0))


    # ----- frame-wise luminance normalization -----
    target_lum = 127.5

    # average luminance across frames
    for i in range(nbframes):

        # get frame luminance
        lum = np.mean(sequence[i])
    
        if lum > 0:
            sequence[i] = sequence[i] * (target_lum / lum)


    return sequence


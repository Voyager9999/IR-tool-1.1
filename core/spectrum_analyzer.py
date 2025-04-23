
import numpy as np
from scipy.signal import savgol_filter, find_peaks
from scipy.ndimage import gaussian_filter1d

class SmartPeakDetector:
    def __init__(self, sensitivity=0.8, min_width=3):
        self.sensitivity = np.clip(sensitivity, 0.1, 1.0)
        self.min_width = min_width
        
    def _adaptive_baseline(self, y):
        iterations = 5
        baseline = y.copy()
        for _ in range(iterations):
            baseline = savgol_filter(baseline, 51, 3)
            baseline = np.minimum(baseline, y)
        return baseline

    def _calculate_noise_level(self, y):
        sorted_y = np.sort(y)
        return np.std(sorted_y[:int(len(y)*0.1)])

    def find_peaks(self, x, y):
        baseline = self._adaptive_baseline(y)
        corrected = y - baseline
        noise_level = self._calculate_noise_level(corrected)
        smoothed = gaussian_filter1d(corrected, sigma=2*(1-self.sensitivity))
        height_threshold = noise_level * 5 * self.sensitivity
        prominence_threshold = noise_level * 3 * self.sensitivity
        
        peaks, properties = find_peaks(
            smoothed,
            height=height_threshold,
            prominence=prominence_threshold,
            width=self.min_width,
            rel_height=0.5
        )
        
        peak_list = []
        for i, pos in enumerate(peaks):
            left = int(properties['left_ips'][i])
            right = int(properties['right_ips'][i])
            peak_data = {
                "position": float(x[pos]),
                "intensity": float(y[pos]),
                "width": float(x[right] - x[left]),
                "area": float(np.trapz(y[left:right], x[left:right])),
                "prominence": float(properties['prominences'][i]),
                "fwhm": float(self._calculate_fwhm(x, y, pos, left, right))
            }
            peak_list.append(peak_data)
        return sorted(peak_list, key=lambda p: p['intensity'], reverse=True)

    def _calculate_fwhm(self, x, y, peak_idx, left, right):
        half_max = y[peak_idx] / 2
        left_idx = np.argmin(np.abs(y[left:peak_idx] - half_max)) + left
        right_idx = np.argmin(np.abs(y[peak_idx:right] - half_max)) + peak_idx
        return float(x[right_idx] - x[left_idx])

//
//  StepDetector.swift
//  StepPhoneClient
//
//  Created by Archit Garg on 12/1/25.
//

import Foundation
import CoreMotion

final class StepDetector {
    private let windowSize: Int
    private let threshold: Double
    private let minStepInterval: TimeInterval

    private var magnitudes: [Double] = []
    private var lastStepTime: TimeInterval?

    init(windowSize: Int = 20,
         threshold: Double = 0.8,
         minStepInterval: TimeInterval = 0.3) {
        self.windowSize = windowSize
        self.threshold = threshold
        self.minStepInterval = minStepInterval
    }

    /// Returns number of steps detected in this sample (0 or 1).
    func update(ax: Double, ay: Double, az: Double, timestamp: TimeInterval) -> Int {
        let mag = sqrt(ax * ax + ay * ay + az * az)

        magnitudes.append(mag)
        if magnitudes.count > windowSize {
            magnitudes.removeFirst()
        }

        guard magnitudes.count == windowSize else {
            return 0
        }

        let avg = magnitudes.reduce(0, +) / Double(magnitudes.count)
        let filtered = mag - avg

        if filtered > threshold {
            if lastStepTime == nil || (timestamp - (lastStepTime ?? 0)) >= minStepInterval {
                lastStepTime = timestamp
                return 1
            }
        }

        return 0
    }
}

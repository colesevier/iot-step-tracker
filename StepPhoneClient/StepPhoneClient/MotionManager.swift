//
//  MotionManager.swift
//  StepPhoneClient
//
//  Created by Archit Garg on 12/1/25.
//

import Foundation
import CoreMotion
import Combine

final class MotionManager: ObservableObject {
    private let motionManager = CMMotionManager()
    private let stepDetector = StepDetector()
    private let apiClient: ApiClient

    @Published var totalSteps: Int = 0
    @Published var unsentSteps: Int = 0
    @Published var lastAlert: String?
    @Published var isRunning: Bool = false

    private let sampleRateHz: Double = 25.0
    private let sendInterval: TimeInterval = 5.0
    private let alertPollInterval: TimeInterval = 5.0

    private var lastSendDate = Date()
    private var lastAlertPollDate = Date()

    init(deviceId: String) {
        self.apiClient = ApiClient(deviceId: deviceId)
    }

    func start() {
        guard !isRunning else { return }
        guard motionManager.isAccelerometerAvailable else {
            print("Accelerometer not available")
            return
        }

        isRunning = true
        totalSteps = 0
        unsentSteps = 0
        lastAlert = nil
        lastSendDate = Date()
        lastAlertPollDate = Date()

        motionManager.accelerometerUpdateInterval = 1.0 / sampleRateHz

        motionManager.startAccelerometerUpdates(to: .main) { [weak self] data, error in
            guard let self = self, let data = data else { return }

            // acceleration is in g; convert to m/s^2
            let ax = data.acceleration.x * 9.81
            let ay = data.acceleration.y * 9.81
            let az = data.acceleration.z * 9.81

            let steps = self.stepDetector.update(
                ax: ax, ay: ay, az: az,
                timestamp: data.timestamp
            )

            if steps > 0 {
                self.totalSteps += steps
                self.unsentSteps += steps
            }

            let now = Date()

            // send steps every sendInterval
            if now.timeIntervalSince(self.lastSendDate) >= self.sendInterval {
                let toSend = max(self.unsentSteps, 1) // send >= 1 so we see something

                self.apiClient.sendSteps(toSend)
                print("DEBUG: Sent \(toSend) steps from iPhone")
                self.unsentSteps = 0
                self.lastSendDate = now
            }
            

            
            // poll alerts every alertPollInterval
            if now.timeIntervalSince(self.lastAlertPollDate) >= self.alertPollInterval {
                self.apiClient.checkAlert { alert in
                    DispatchQueue.main.async {
                        if let alert = alert {
                            print("ALERT from server:", alert)
                            self.lastAlert = alert
                            // TODO: add haptic/vibration if you want
                        }
                    }
                }
                self.lastAlertPollDate = now
            }
        }
    }

    func stop() {
        guard isRunning else { return }
        motionManager.stopAccelerometerUpdates()
        isRunning = false
    }
}

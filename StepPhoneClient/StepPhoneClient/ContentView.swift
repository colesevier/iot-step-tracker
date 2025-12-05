//
//  ContentView.swift
//  StepPhoneClient
//
//  Created by Archit Garg on 12/1/25.
//

import SwiftUI

struct ContentView: View {
    // Make sure this deviceId matches what your Python server/UI use
    @StateObject private var motionManager = MotionManager(deviceId: "iphone_1")

    var body: some View {
        VStack(spacing: 16) {
            Text("iPhone Step Client")
                .font(.title)
                .padding(.bottom, 8)

            Text("Total steps (since start): \(motionManager.totalSteps)")
                .font(.headline)

            Text("Unsent steps: \(motionManager.unsentSteps)")
                .font(.subheadline)
                .foregroundColor(.secondary)

            if let alert = motionManager.lastAlert {
                Text("Alert: \(alert)")
                    .foregroundColor(.red)
                    .padding(.top, 8)
            }

            Button(motionManager.isRunning ? "Stop" : "Start") {
                if motionManager.isRunning {
                    motionManager.stop()
                } else {
                    motionManager.start()
                }
            }
            .buttonStyle(.borderedProminent)
            .padding(.top, 16)

            Spacer()
        }
        .padding()
    }
}

#Preview {
    ContentView()
}

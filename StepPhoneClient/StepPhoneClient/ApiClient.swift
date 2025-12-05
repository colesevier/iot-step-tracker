//
//  ApiClient.swift
//  StepPhoneClient
//
//  Created by Archit Garg on 12/1/25.
//

import Foundation

struct StepPayload: Codable {
    let device_id: String
    let steps: Int
    let timestamp: String
}

struct AlertResponse: Codable {
    let alert: String?
}

final class ApiClient {
   
    //private let BASE_URL_STRING = "http://MAC_IP:8000"
    private let BASE_URL_STRING = "http://10.23.2.195:8000"

    private let deviceId: String
    private let isoFormatter = ISO8601DateFormatter()

    init(deviceId: String) {
        self.deviceId = deviceId
    }

    private var baseURL: URL {
        return URL(string: BASE_URL_STRING)!
    }

    func sendSteps(_ steps: Int) {
        guard steps > 0 else { return }

        var request = URLRequest(url: baseURL.appendingPathComponent("data"))
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = StepPayload(
            device_id: deviceId,
            steps: steps,
            timestamp: isoFormatter.string(from: Date())
        )

        do {
            request.httpBody = try JSONEncoder().encode(payload)
        } catch {
            print("Encoding error:", error)
            return
        }

        URLSession.shared.dataTask(with: request) { _, _, error in
            if let error = error {
                print("sendSteps error:", error)
            }
        }.resume()
    }

    func checkAlert(completion: @escaping (String?) -> Void) {
        let url = baseURL.appendingPathComponent("alert/\(deviceId)")

        URLSession.shared.dataTask(with: url) { data, _, error in
            if let error = error {
                print("checkAlert error:", error)
                completion(nil)
                return
            }

            guard let data = data else {
                completion(nil)
                return
            }

            do {
                let resp = try JSONDecoder().decode(AlertResponse.self, from: data)
                completion(resp.alert)
            } catch {
                print("Alert decode error:", error)
                completion(nil)
            }
        }.resume()
    }
}

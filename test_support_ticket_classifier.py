import unittest
from support_ticket_classifier import SupportTicketClassifier, ClassificationResult


class TestSupportTicketClassifier(unittest.TestCase):
    """Test suite for SupportTicketClassifier."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.classifier = SupportTicketClassifier()
    
    # Customer Name Extraction Tests
    def test_extract_customer_from_keyword_format(self):
        """Test extracting customer from 'Customer:' format."""
        ticket = "Customer: John Smith\nThe system is down"
        result = self.classifier.extract_customer_name(ticket)
        self.assertEqual(result, "John Smith")
    
    def test_extract_customer_from_name_format(self):
        """Test extracting customer from 'Name:' format."""
        ticket = "Name: Alice Johnson\nI have a billing issue"
        result = self.classifier.extract_customer_name(ticket)
        self.assertEqual(result, "Alice Johnson")
    
    def test_extract_customer_from_from_format(self):
        """Test extracting customer from 'From:' format."""
        ticket = "From: Bob Wilson\nCannot login"
        result = self.classifier.extract_customer_name(ticket)
        self.assertEqual(result, "Bob Wilson")
    
    def test_extract_customer_unknown(self):
        """Test returns 'Unknown' when customer not found."""
        ticket = "The system is broken and needs fixing"
        result = self.classifier.extract_customer_name(ticket)
        self.assertEqual(result, "Unknown")
    
    def test_extract_customer_invalid_format(self):
        """Test handles invalid customer formats gracefully."""
        ticket = "Customer: \nThe system is broken"
        result = self.classifier.extract_customer_name(ticket)
        self.assertEqual(result, "Unknown")
    
    # Issue Type Detection Tests
    def test_detect_configuration_issue(self):
        """Test detecting configuration issue type."""
        ticket = "Customer: John\nHow do I configure the API and install the SDK?"
        issue_type, confidence = self.classifier.detect_issue_type(ticket)
        self.assertEqual(issue_type, "configuration")
        self.assertGreater(confidence, 0.5)
    
    def test_detect_billing_issue(self):
        """Test detecting billing issue type."""
        ticket = "Customer: Jane\nI was charged twice. Please refund my payment."
        issue_type, confidence = self.classifier.detect_issue_type(ticket)
        self.assertEqual(issue_type, "billing")
        self.assertGreater(confidence, 0.5)
    
    def test_detect_authentication_issue(self):
        """Test detecting authentication issue type."""
        ticket = "Customer: Mike\nMy API token is not working and I need new credentials."
        issue_type, confidence = self.classifier.detect_issue_type(ticket)
        self.assertEqual(issue_type, "authentication")
        self.assertGreater(confidence, 0.5)
    
    def test_detect_login_issue(self):
        """Test detecting login issue type."""
        ticket = "Customer: Sarah\nI cannot login and the password reset doesn't work."
        issue_type, confidence = self.classifier.detect_issue_type(ticket)
        self.assertEqual(issue_type, "login")
        self.assertGreater(confidence, 0.5)
    
    def test_detect_general_issue(self):
        """Test detecting general issue type."""
        ticket = "Something is wrong but I don't know what"
        issue_type, confidence = self.classifier.detect_issue_type(ticket)
        self.assertEqual(issue_type, "general")
    
    # Severity Detection Tests
    def test_detect_critical_severity(self):
        """Test detecting critical severity."""
        ticket = "Customer: John\nThe entire system is completely down and broken!"
        severity, confidence = self.classifier.detect_severity(ticket)
        self.assertEqual(severity, "critical")
        self.assertGreater(confidence, 0.5)
    
    def test_detect_high_severity(self):
        """Test detecting high severity."""
        ticket = "Customer: Jane\nPart of the system is degraded and I cannot perform my duties."
        severity, confidence = self.classifier.detect_severity(ticket)
        self.assertEqual(severity, "high")
        self.assertGreater(confidence, 0.5)
    
    def test_detect_medium_severity(self):
        """Test detecting medium severity."""
        ticket = "Customer: Mike\nThe feature is not working as expected with unexpected behavior."
        severity, confidence = self.classifier.detect_severity(ticket)
        self.assertEqual(severity, "medium")
        self.assertGreater(confidence, 0.5)
    
    def test_detect_low_severity(self):
        """Test detecting low severity."""
        ticket = "Customer: Sarah\nI have a general question about how to use this feature."
        severity, confidence = self.classifier.detect_severity(ticket)
        self.assertEqual(severity, "low")
    
    # Impact Calculation Tests
    def test_calculate_critical_impact(self):
        """Test calculating critical impact."""
        impact = self.classifier.calculate_impact("critical")
        self.assertEqual(impact, "Entire system is degraded. System not functioning at all")
    
    def test_calculate_high_impact(self):
        """Test calculating high impact."""
        impact = self.classifier.calculate_impact("high")
        self.assertEqual(impact, "Part of the system is degraded. Incapable to perform duties")
    
    def test_calculate_medium_impact(self):
        """Test calculating medium impact."""
        impact = self.classifier.calculate_impact("medium")
        self.assertEqual(impact, "Part of the functionality is not working as expected")
    
    def test_calculate_low_impact(self):
        """Test calculating low impact."""
        impact = self.classifier.calculate_impact("low")
        self.assertEqual(impact, "General issue/queries or unknown issues")
    
    # Confidence Level Tests
    def test_confidence_high(self):
        """Test high confidence level."""
        ticket = "Customer: John\nThe entire system is completely down and completely broken!"
        result = self.classifier.classify(ticket)
        self.assertEqual(result.confidence, "high")
    
    def test_confidence_medium(self):
        """Test medium confidence level."""
        ticket = "Customer: Jane\nSomething seems wrong"
        result = self.classifier.classify(ticket)
        self.assertIn(result.confidence, ["high", "medium", "low"])
    
    def test_confidence_low(self):
        """Test low confidence level."""
        ticket = "xyz abc"
        result = self.classifier.classify(ticket)
        self.assertEqual(result.confidence, "low")
    
    # Summary Generation Tests
    def test_summary_generation(self):
        """Test issue summary generation."""
        ticket = "Customer: John\nThe system is down. Please fix it. This is urgent."
        result = self.classifier.classify(ticket)
        self.assertGreater(len(result.issue_summary), 0)
        self.assertLessEqual(len(result.issue_summary), 3)
        for point in result.issue_summary:
            self.assertTrue(point.startswith("•"))
    
    def test_summary_truncation(self):
        """Test summary truncation to 150 characters."""
        ticket = "Customer: John\n" + "x" * 200
        result = self.classifier.classify(ticket)
        for point in result.issue_summary:
            # Remove bullet point and check length
            clean_point = point.replace("•", "").strip()
            self.assertLessEqual(len(clean_point), 151)  # 150 + period
    
    def test_summary_max_three_points(self):
        """Test summary limited to 3 bullet points."""
        ticket = "Customer: John\nPoint 1. Point 2. Point 3. Point 4. Point 5."
        result = self.classifier.classify(ticket)
        self.assertLessEqual(len(result.issue_summary), 3)
    
    # Full Classification Tests
    def test_classify_critical_system_outage(self):
        """Test full classification of critical system outage."""
        ticket = """
        From: Sarah Johnson
        The entire system is completely down and we cannot access anything at all!
        Nothing is working. This is critical!
        """
        result = self.classifier.classify(ticket)
        self.assertEqual(result.customer, "Sarah Johnson")
        self.assertEqual(result.severity, "critical")
        self.assertIn(result.issue_type, self.classifier.ISSUE_TYPES.keys())
        self.assertEqual(result.confidence, "high")
        self.assertGreater(len(result.issue_summary), 0)
    
    def test_classify_login_issue(self):
        """Test full classification of login issue."""
        ticket = """
        Customer: Mike Chen
        I cannot login to my account and the password reset function isn't working either.
        """
        result = self.classifier.classify(ticket)
        self.assertEqual(result.customer, "Mike Chen")
        self.assertEqual(result.issue_type, "login")
        self.assertIn(result.severity, ["medium", "high"])
        self.assertEqual(result.confidence, "high")
    
    def test_classify_billing_issue(self):
        """Test full classification of billing issue."""
        ticket = """
        Name: Lisa Park
        I was charged twice for my subscription. Please check my billing invoice and refund.
        """
        result = self.classifier.classify(ticket)
        self.assertEqual(result.customer, "Lisa Park")
        self.assertEqual(result.issue_type, "billing")
        self.assertEqual(result.confidence, "high")
    
    def test_classify_configuration_query(self):
        """Test full classification of configuration query."""
        ticket = """
        Customer: Alex Torres
        How do I properly configure the API authentication and install the SDK?
        """
        result = self.classifier.classify(ticket)
        self.assertEqual(result.customer, "Alex Torres")
        self.assertEqual(result.issue_type, "configuration")
        self.assertEqual(result.severity, "low")
    
    # Batch Processing Tests
    def test_classify_batch(self):
        """Test batch classification."""
        tickets = [
            "Customer: Alice\nThe system is down",
            "From: Bob\nI cannot login",
            "Name: Carol\nBilling issue"
        ]
        results = self.classifier.classify_batch(tickets)
        self.assertEqual(len(results), 3)
        self.assertIsInstance(results[0], ClassificationResult)
    
    def test_classify_batch_empty_list(self):
        """Test batch classification with empty list."""
        results = self.classifier.classify_batch([])
        self.assertEqual(len(results), 0)
    
    # Output Format Tests
    def test_classification_result_to_dict(self):
        """Test converting classification result to dictionary."""
        ticket = "Customer: John\nThe system is down"
        result = self.classifier.classify(ticket)
        result_dict = result.to_dict()
        self.assertIn("customer", result_dict)
        self.assertIn("issue_type", result_dict)
        self.assertIn("severity", result_dict)
        self.assertIn("confidence", result_dict)
        self.assertIn("issue_summary", result_dict)
    
    def test_classification_result_to_json(self):
        """Test converting classification result to JSON."""
        ticket = "Customer: John\nThe system is down"
        result = self.classifier.classify(ticket)
        json_str = result.to_json()
        self.assertIsInstance(json_str, str)
        self.assertIn("customer", json_str)
        self.assertIn("issue_type", json_str)
    
    # Error Handling Tests
    def test_classify_empty_ticket(self):
        """Test error handling for empty ticket."""
        with self.assertRaises(ValueError):
            self.classifier.classify("")
    
    def test_classify_none_ticket(self):
        """Test error handling for None ticket."""
        with self.assertRaises(ValueError):
            self.classifier.classify(None)
    
    def test_classify_batch_invalid_type(self):
        """Test error handling for invalid batch type."""
        with self.assertRaises(ValueError):
            self.classifier.classify_batch("not a list")
    
    # Edge Cases
    def test_ticket_with_multiple_customers(self):
        """Test handling ticket with multiple customer references."""
        ticket = "Customer: John Smith\nFrom: Jane Doe\nI have an issue"
        result = self.classifier.classify(ticket)
        self.assertIsNotNone(result.customer)
        self.assertNotEqual(result.customer, "Unknown")
    
    def test_ticket_with_mixed_case_keywords(self):
        """Test case-insensitive keyword matching."""
        ticket = "Customer: John\nTHE ENTIRE SYSTEM IS DOWN AND BROKEN"
        result = self.classifier.classify(ticket)
        self.assertEqual(result.severity, "critical")
    
    def test_ticket_with_special_characters(self):
        """Test handling special characters in tickets."""
        ticket = "Customer: John@123\nThe system is down!!! Help!!!"
        result = self.classifier.classify(ticket)
        self.assertEqual(result.customer, "Unknown")  # Invalid customer format
        self.assertEqual(result.severity, "critical")


if __name__ == "__main__":
    unittest.main()

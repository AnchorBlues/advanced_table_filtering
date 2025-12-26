"""Integration tests for filter application."""

import unittest
import pandas as pd
from pathlib import Path

# Integration tests will use actual filter engine and data processing
try:
    from src.lib.filter_engine import apply_single_filter, apply_multiple_filters
    from src.lib.data_processor import prepare_table_data, convert_to_json_format
except ImportError:
    # Placeholder for TDD - tests should fail initially
    apply_single_filter = None
    apply_multiple_filters = None
    prepare_table_data = None
    convert_to_json_format = None


class TestFilterApplication(unittest.TestCase):
    """Integration tests for filter application flow."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.fixtures_dir = Path(__file__).parent.parent / "fixtures"
        cls.sample_csv = cls.fixtures_dir / "sample.csv"
    
    def setUp(self):
        """Set up test data."""
        self.sample_df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'Age': [25, 30, 35, 28, 32],
            'Amount': [1000.5, 2000.0, 1500.75, 3000.0, 2500.5],
            'Status': ['Active', 'Inactive', 'Active', 'Active', 'Inactive'],
            'City': ['Tokyo', 'Osaka', 'Tokyo', 'Kyoto', 'Osaka']
        })
    
    def test_apply_text_filter(self):
        """
        Test complete flow: Load data → Apply text filter → Verify results.
        
        This test verifies the end-to-end flow from data preparation
        to filter application and result verification.
        """
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Prepare table data (simulating upload flow)
        table_data = prepare_table_data(self.sample_df, 'csv', 'test.csv')
        
        # Verify data is prepared correctly
        self.assertIn('dataframe_json', table_data, "Table data should contain dataframe_json")
        self.assertEqual(len(table_data['dataframe_json']), 5, "Should have 5 rows")
        
        # Apply filter: Status equals 'Active'
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Status',
            operator='equals',
            value='Active',
            data_type='text'
        )
        
        # Verify filter results
        self.assertEqual(len(filtered_df), 3, "Should have 3 matching rows")
        self.assertTrue(all(status == 'Active' for status in filtered_df['Status']), "All statuses should be 'Active'")
        
        # Convert filtered results to JSON format (for display)
        filtered_json = convert_to_json_format(filtered_df)
        self.assertEqual(len(filtered_json), 3, "Filtered JSON should have 3 records")
    
    def test_apply_numeric_filter(self):
        """
        Test complete flow: Load data → Apply numeric filter → Verify results.
        
        This test verifies the end-to-end flow for numeric filtering.
        """
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Prepare table data
        table_data = prepare_table_data(self.sample_df, 'csv', 'test.csv')
        
        # Apply filter: Amount greater than 2000
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Amount',
            operator='greater_than',
            value=2000,
            data_type='numeric'
        )
        
        # Verify filter results
        self.assertEqual(len(filtered_df), 2, "Should have 2 matching rows")
        self.assertTrue(all(amount > 2000 for amount in filtered_df['Amount']), "All amounts should be > 2000")
        
        # Verify row count update
        original_count = len(self.sample_df)
        filtered_count = len(filtered_df)
        self.assertLess(filtered_count, original_count, "Filtered count should be less than original")
    
    def test_and_combination(self):
        """
        Test complete flow: Load data → Apply multiple filters with AND logic → Verify results.
        
        This test verifies the end-to-end flow for AND filter combination.
        """
        self.assertIsNotNone(apply_multiple_filters, "apply_multiple_filters function should be implemented")
        
        if apply_multiple_filters is None:
            self.skipTest("apply_multiple_filters not implemented yet")
        
        # Prepare table data
        table_data = prepare_table_data(self.sample_df, 'csv', 'test.csv')
        
        # Apply filters: Status = 'Active' AND City = 'Tokyo'
        conditions = [
            {
                'column_name': 'Status',
                'operator': 'equals',
                'value': 'Active',
                'data_type': 'text'
            },
            {
                'column_name': 'City',
                'operator': 'equals',
                'value': 'Tokyo',
                'data_type': 'text'
            }
        ]
        
        filtered_df = apply_multiple_filters(self.sample_df, conditions, logic_operator='AND')
        
        # Verify filter results
        self.assertEqual(len(filtered_df), 2, "Should have 2 matching rows (Alice and Charlie)")
        self.assertTrue(all(row['Status'] == 'Active' and row['City'] == 'Tokyo' 
                           for _, row in filtered_df.iterrows()), 
                       "All rows should match both conditions")
        
        # Convert filtered results to JSON format
        filtered_json = convert_to_json_format(filtered_df)
        self.assertEqual(len(filtered_json), 2, "Filtered JSON should have 2 records")
    
    def test_or_combination(self):
        """
        Test complete flow: Load data → Apply multiple filters with OR logic → Verify results.
        
        This test verifies the end-to-end flow for OR filter combination.
        """
        self.assertIsNotNone(apply_multiple_filters, "apply_multiple_filters function should be implemented")
        
        if apply_multiple_filters is None:
            self.skipTest("apply_multiple_filters not implemented yet")
        
        # Prepare table data
        table_data = prepare_table_data(self.sample_df, 'csv', 'test.csv')
        
        # Apply filters: City = 'Tokyo' OR City = 'Kyoto'
        conditions = [
            {
                'column_name': 'City',
                'operator': 'equals',
                'value': 'Tokyo',
                'data_type': 'text'
            },
            {
                'column_name': 'City',
                'operator': 'equals',
                'value': 'Kyoto',
                'data_type': 'text'
            }
        ]
        
        filtered_df = apply_multiple_filters(self.sample_df, conditions, logic_operator='OR')
        
        # Verify filter results
        self.assertEqual(len(filtered_df), 3, "Should have 3 matching rows (Tokyo: Alice, Charlie; Kyoto: David)")
        self.assertTrue(all(row['City'] in ['Tokyo', 'Kyoto'] 
                           for _, row in filtered_df.iterrows()), 
                       "All rows should match either condition")
        
        # Verify row count update
        original_count = len(self.sample_df)
        filtered_count = len(filtered_df)
        self.assertLess(filtered_count, original_count, "Filtered count should be less than original")


if __name__ == '__main__':
    unittest.main()


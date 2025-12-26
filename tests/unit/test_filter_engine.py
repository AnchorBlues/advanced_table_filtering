"""Unit tests for filter engine module."""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, date

from src.lib.filter_engine import (
    apply_single_filter,
    validate_filter_operator,
    apply_text_filter,
    apply_numeric_filter,
    apply_date_filter,
    apply_multiple_filters
)


class TestFilterEngine(unittest.TestCase):
    """Test cases for filter engine functions."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'Age': [25, 30, 35, 28, 32],
            'Amount': [1000.5, 2000.0, 1500.75, 3000.0, 2500.5],
            'Date': pd.to_datetime(['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01', '2024-05-01']),
            'Status': ['Active', 'Inactive', 'Active', 'Active', 'Inactive'],
            'City': ['Tokyo', 'Osaka', 'Tokyo', 'Kyoto', 'Osaka']
        })
    
    # Text filter tests
    def test_text_equals(self):
        """Test text equals filter operation."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Filter: Name equals 'Alice'
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Name',
            operator='equals',
            value='Alice',
            data_type='text'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 1, "Should have 1 matching row")
        self.assertEqual(filtered_df.iloc[0]['Name'], 'Alice', "Should match 'Alice'")
    
    def test_text_contains(self):
        """Test text contains filter operation."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Filter: City contains 'Tok'
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='City',
            operator='contains',
            value='Tok',
            data_type='text'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 2, "Should have 2 matching rows (Tokyo)")
        self.assertTrue(all('Tok' in city for city in filtered_df['City']), "All cities should contain 'Tok'")
    
    def test_text_starts_with(self):
        """Test text starts_with filter operation."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Filter: Name starts with 'C'
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Name',
            operator='starts_with',
            value='C',
            data_type='text'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 1, "Should have 1 matching row (Charlie)")
        self.assertTrue(filtered_df.iloc[0]['Name'].startswith('C'), "Name should start with 'C'")
    
    def test_text_ends_with(self):
        """Test text ends_with filter operation."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Filter: Status ends with 'e'
        # Note: Both 'Active' and 'Inactive' end with 'e', so we expect 5 rows
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Status',
            operator='ends_with',
            value='e',
            data_type='text'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 5, "Should have 5 matching rows (both Active and Inactive end with 'e')")
        self.assertTrue(all(status.endswith('e') for status in filtered_df['Status']), "All statuses should end with 'e'")
    
    # Numeric filter tests
    def test_numeric_equals(self):
        """Test numeric equals filter operation."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Filter: Age equals 30
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Age',
            operator='equals',
            value=30,
            data_type='numeric'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 1, "Should have 1 matching row")
        self.assertEqual(filtered_df.iloc[0]['Age'], 30, "Age should equal 30")
    
    def test_numeric_greater_than(self):
        """Test numeric greater_than filter operation."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Filter: Amount greater than 2000
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Amount',
            operator='greater_than',
            value=2000,
            data_type='numeric'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 2, "Should have 2 matching rows")
        self.assertTrue(all(amount > 2000 for amount in filtered_df['Amount']), "All amounts should be > 2000")
    
    def test_numeric_less_than(self):
        """Test numeric less_than filter operation."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Filter: Age less than 30
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Age',
            operator='less_than',
            value=30,
            data_type='numeric'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 2, "Should have 2 matching rows (Age=25 and Age=28)")
        self.assertTrue(all(age < 30 for age in filtered_df['Age']), "All ages should be < 30")
    
    def test_numeric_between(self):
        """Test numeric between filter operation."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Filter: Amount between 1500 and 2500
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Amount',
            operator='between',
            value=(1500, 2500),
            data_type='numeric'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 2, "Should have 2 matching rows")
        self.assertTrue(all(1500 <= amount <= 2500 for amount in filtered_df['Amount']), "All amounts should be between 1500 and 2500")
    
    # Date filter tests
    def test_date_equals(self):
        """Test date equals filter operation."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Filter: Date equals '2024-03-01'
        target_date = pd.to_datetime('2024-03-01')
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Date',
            operator='equals',
            value=target_date,
            data_type='date'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 1, "Should have 1 matching row")
        self.assertTrue((filtered_df['Date'] == target_date).all(), "All dates should equal target date")
    
    def test_date_before(self):
        """Test date before filter operation."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Filter: Date before '2024-03-01'
        target_date = pd.to_datetime('2024-03-01')
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Date',
            operator='before',
            value=target_date,
            data_type='date'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 2, "Should have 2 matching rows")
        self.assertTrue(all(date < target_date for date in filtered_df['Date']), "All dates should be before target date")
    
    def test_date_after(self):
        """Test date after filter operation."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Filter: Date after '2024-03-01'
        target_date = pd.to_datetime('2024-03-01')
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Date',
            operator='after',
            value=target_date,
            data_type='date'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 2, "Should have 2 matching rows")
        self.assertTrue(all(date > target_date for date in filtered_df['Date']), "All dates should be after target date")
    
    def test_date_between(self):
        """Test date between filter operation."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Filter: Date between '2024-02-01' and '2024-04-01'
        start_date = pd.to_datetime('2024-02-01')
        end_date = pd.to_datetime('2024-04-01')
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Date',
            operator='between',
            value=(start_date, end_date),
            data_type='date'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 3, "Should have 3 matching rows")
        self.assertTrue(all(start_date <= date <= end_date for date in filtered_df['Date']), "All dates should be between start and end date")
    
    def test_text_equals_multi(self):
        """Test text equals filter with multiple values (list)."""
        # Filter: City equals ['Tokyo', 'Osaka']
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='City',
            operator='equals',
            value=['Tokyo', 'Osaka'],
            data_type='text'
        )
        
        self.assertEqual(len(filtered_df), 4, "Should have 4 matching rows (Tokyo and Osaka)")
        self.assertTrue(all(city in ['Tokyo', 'Osaka'] for city in filtered_df['City']))

    def test_numeric_equals_multi(self):
        """Test numeric equals filter with multiple values (list)."""
        # Filter: Age equals [25, 30]
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Age',
            operator='equals',
            value=[25, 30],
            data_type='numeric'
        )
        
        self.assertEqual(len(filtered_df), 2, "Should have 2 matching rows")
        self.assertTrue(all(age in [25, 30] for age in filtered_df['Age']))

    def test_date_equals_multi(self):
        """Test date equals filter with multiple values (list)."""
        # Filter: Date equals ['2024-01-01', '2024-03-01']
        dates = [pd.to_datetime('2024-01-01'), pd.to_datetime('2024-03-01')]
        filtered_df = apply_single_filter(
            self.sample_df,
            column_name='Date',
            operator='equals',
            value=dates,
            data_type='date'
        )
        
        self.assertEqual(len(filtered_df), 2, "Should have 2 matching rows")
        self.assertTrue(all(d.date() in [dates[0].date(), dates[1].date()] for d in filtered_df['Date']))

    # Null value handling tests
    def test_null_value_handling(self):
        """Test null value handling in filters."""
        self.assertIsNotNone(apply_single_filter, "apply_single_filter function should be implemented")
        
        if apply_single_filter is None:
            self.skipTest("apply_single_filter not implemented yet")
        
        # Create DataFrame with null values
        df_with_nulls = pd.DataFrame({
            'Name': ['Alice', 'Bob', None, 'David'],
            'Age': [25, 30, None, 28],
            'Amount': [1000.5, None, 1500.75, 3000.0]
        })
        
        # Filter: Name equals 'Alice' (should exclude nulls)
        filtered_df = apply_single_filter(
            df_with_nulls,
            column_name='Name',
            operator='equals',
            value='Alice',
            data_type='text'
        )
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), 1, "Should have 1 matching row")
        self.assertFalse(filtered_df['Name'].isna().any(), "Should not include null values")
    
    # Multiple filter tests (Phase 5)
    def test_multiple_filters_and_logic(self):
        """Test multiple filters with AND logic."""
        self.assertIsNotNone(apply_multiple_filters, "apply_multiple_filters function should be implemented")
        
        if apply_multiple_filters is None:
            self.skipTest("apply_multiple_filters not implemented yet")
        
        # Filter: Status = 'Active' AND Age = 30
        conditions = [
            {
                'column_name': 'Status',
                'operator': 'equals',
                'value': 'Active',
                'data_type': 'text'
            },
            {
                'column_name': 'Age',
                'operator': 'equals',
                'value': 30,
                'data_type': 'numeric'
            }
        ]
        
        filtered_df = apply_multiple_filters(self.sample_df, conditions, logic_operator='AND')
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        # No row matches both conditions (Status='Active' AND Age=30)
        # Bob has Age=30 but Status='Inactive'
        # Alice, Charlie, David have Status='Active' but Age != 30
        self.assertEqual(len(filtered_df), 0, "Should have 0 matching rows (no row matches both conditions)")
    
    def test_multiple_filters_and_logic_with_match(self):
        """Test multiple filters with AND logic that has matches."""
        self.assertIsNotNone(apply_multiple_filters, "apply_multiple_filters function should be implemented")
        
        if apply_multiple_filters is None:
            self.skipTest("apply_multiple_filters not implemented yet")
        
        # Filter: Status = 'Active' AND City = 'Tokyo'
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
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        # Alice and Charlie match: Status='Active' AND City='Tokyo'
        self.assertEqual(len(filtered_df), 2, "Should have 2 matching rows")
        self.assertTrue(all(row['Status'] == 'Active' and row['City'] == 'Tokyo' 
                           for _, row in filtered_df.iterrows()), 
                       "All rows should match both conditions")
    
    def test_multiple_filters_or_logic(self):
        """Test multiple filters with OR logic."""
        self.assertIsNotNone(apply_multiple_filters, "apply_multiple_filters function should be implemented")
        
        if apply_multiple_filters is None:
            self.skipTest("apply_multiple_filters not implemented yet")
        
        # Filter: City = 'Tokyo' OR City = 'Kyoto'
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
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        # Alice, Charlie (Tokyo), David (Kyoto) match
        self.assertEqual(len(filtered_df), 3, "Should have 3 matching rows")
        self.assertTrue(all(row['City'] in ['Tokyo', 'Kyoto'] 
                           for _, row in filtered_df.iterrows()), 
                       "All rows should match either condition")
    
    def test_multiple_filters_or_logic_different_columns(self):
        """Test multiple filters with OR logic across different columns."""
        self.assertIsNotNone(apply_multiple_filters, "apply_multiple_filters function should be implemented")
        
        if apply_multiple_filters is None:
            self.skipTest("apply_multiple_filters not implemented yet")
        
        # Filter: Age = 25 OR Amount > 2500
        conditions = [
            {
                'column_name': 'Age',
                'operator': 'equals',
                'value': 25,
                'data_type': 'numeric'
            },
            {
                'column_name': 'Amount',
                'operator': 'greater_than',
                'value': 2500,
                'data_type': 'numeric'
            }
        ]
        
        filtered_df = apply_multiple_filters(self.sample_df, conditions, logic_operator='OR')
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        # Alice (Age=25) OR David (Amount=3000.0 > 2500) OR Eve (Amount=2500.5 > 2500) match
        self.assertEqual(len(filtered_df), 3, "Should have 3 matching rows")
        self.assertTrue(all(row['Age'] == 25 or row['Amount'] > 2500 
                           for _, row in filtered_df.iterrows()), 
                       "All rows should match either condition")
    
    def test_multiple_filters_empty_conditions(self):
        """Test multiple filters with empty conditions list."""
        self.assertIsNotNone(apply_multiple_filters, "apply_multiple_filters function should be implemented")
        
        if apply_multiple_filters is None:
            self.skipTest("apply_multiple_filters not implemented yet")
        
        # Empty conditions should return original DataFrame
        filtered_df = apply_multiple_filters(self.sample_df, [], logic_operator='AND')
        
        self.assertIsInstance(filtered_df, pd.DataFrame, "Should return DataFrame")
        self.assertEqual(len(filtered_df), len(self.sample_df), "Should return all rows when no conditions")
    
    def test_multiple_filters_max_conditions_limit(self):
        """Test that maximum 10 conditions are allowed."""
        self.assertIsNotNone(apply_multiple_filters, "apply_multiple_filters function should be implemented")
        
        if apply_multiple_filters is None:
            self.skipTest("apply_multiple_filters not implemented yet")
        
        # Create 11 conditions (exceeds limit)
        conditions = [
            {
                'column_name': 'Status',
                'operator': 'equals',
                'value': 'Active',
                'data_type': 'text'
            }
        ] * 11
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            apply_multiple_filters(self.sample_df, conditions, logic_operator='AND')


if __name__ == '__main__':
    unittest.main()


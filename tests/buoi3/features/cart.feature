
Feature: Shopping cart calculation
  As a shopper
  I want to add products to my cart
  So that I can verify the correct total price

  Background:
    Given I am on the home page

  Scenario Outline: Cart calculates the correct price
    When I open the product "<product>"
    And I add it to the cart with quantity <quantity>
    Then the cart line price equals the unit price times <quantity>
    And the cart total equals the sum of the line prices

    Examples:
      | product            | quantity |
      | Combination Pliers | 1        |
      | Claw Hammer        | 3        |

Feature: Purchase a product
        @purchase
        Scenario: Add product to cart
             When user is on the product page
              And user subscribes to product
              And user adds the product to the cart
             Then user is on the cart page
              And user sees the message "Item has been added to cart"
              And the purchase type is "Subscribe & Save"

        @faq
        Scenario: Verify FAQ accordion functionality
            Given user is on the FAQ section
             When user clicks on accordion button 1
             Then accordion section 1 should be expanded
              And only one accordion section should be expanded
             When user clicks on accordion button 2
             Then accordion section 2 should be expanded
              And accordion section 1 should be collapsed
              And only one accordion section should be expanded
             When user clicks on accordion button 2
             Then accordion section 2 should be collapsed

        @cart
        Scenario: Verify Cart Functionality
            Given user is on the cart page
             Then user should see the cart title "Your Shopping Cart"
              And user should see the product "Nature's Gift Bone Broth" with correct image and description
             When user increases the quantity to 3
             Then the total price should be updated correctly
             When user decreases the quantity to 1
             Then the total price should be updated correctly
             When user removes the item
             Then the cart should be empty
             When user adds the product "Nature's Gift Bone Broth" to the cart
             And user applies a valid coupon code "VALIDCOUPON"
             Then the discount should be applied
             When user applies an invalid coupon code "INVALID"
             Then an error message should be displayed
             When user proceeds to checkout
             Then user should be on the checkout page
             When user tries to proceed to checkout with an empty cart
             Then user should be prevented from proceeding
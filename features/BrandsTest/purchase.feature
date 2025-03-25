Feature: Product Purchase Flow

        Background:
            Given the website is accessible

        @purchase @smoke
        Scenario: Subscribe to product and add to cart
            Given user is on the product page
             When user subscribes to product
              And user adds the product to the cart
             Then user is on the cart page
              And user sees the message "Item has been added to cart"
              And the purchase type is "Subscribe & Save"

        @cart @smoke
        Scenario: Apply discount coupon to cart
            Given user is on the product page
             When user adds the product to the cart
              And user is on the cart page
              And user applies a valid coupon code "AEONS15"
             Then the discount should be applied
              And user proceeds to checkout

        @faq
        Scenario Outline: Verify FAQ accordion functionality
            Given user is on the FAQ section
             When user clicks on accordion button <button_number>
             Then accordion section <button_number> should be expanded
              And only one accordion section should be expanded

        Examples:
                  | button_number |
                  | 1             |
                  | 2             |
                  | 3             |

        @cart @negative
        Scenario: Verify cart error handling
            Given user is on the cart page
             Then the cart should be empty
             When user applies a valid coupon code "INVALID"
             Then user should see an error message "Invalid coupon code"
              And user should be prevented from proceeding to checkout

        @purchase @regression
        Scenario: Complete purchase flow with subscription
            Given user is on the product page
             When user subscribes to product
              And user adds the product to the cart
             Then user is on the cart page
             When user applies a valid coupon code "AEONS15"
             Then the discount should be applied
             When user proceeds to checkout
             Then user should be on the checkout page
             When user fills out the checkout form with valid details
             Then the purchase should be successfully completed
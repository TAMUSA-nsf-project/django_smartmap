// Tell me of any naming suggestions for my files and variables.
// I am aware they can be rather awkward.

//	This is what is called a "JavaScript closure". It prevents variables from
//	being entirely global by encasing them inside a parent function.
//	It's kinda like the 'protected' keyword from the Java language.
(function()
{
	let LEFT_DRAWER,			// All of these are treated as constants
		RIGHT_DRAWER,			// even though their types are 'let'
		DRAWER_BACKDROP,
		LEFT_DRAWER_OPEN_POSITION,
		LEFT_DRAWER_CLOSED_POSITION,
		RIGHT_DRAWER_OPEN_POSITION,
		RIGHT_DRAWER_CLOSED_POSITION;

	$(document).ready(function()
	{
		LEFT_DRAWER		= $("#MapDrawerLeft");
		RIGHT_DRAWER	= $("#MapDrawerRight");
		DRAWER_BACKDROP	= $("#MapDrawerBackdrop");
		LEFT_DRAWER_CLOSED_POSITION		= LEFT_DRAWER.width() * -1;
		LEFT_DRAWER_OPEN_POSITION		= 0;
		RIGHT_DRAWER_CLOSED_POSITION	= RIGHT_DRAWER.width() * -1;
		RIGHT_DRAWER_OPEN_POSITION		= 0;
	});

	// These two functions are only to be used inside the 'DrawerOpenOrClose' function
	function LeftDrawerSetXPosition( setXPos ) {
		LEFT_DRAWER.animate(
			{
				marginLeft: setXPos + 'px'	// CSS properties are camelCase in jQ's animate
			},
			{
				duration: 35,
				easing: 'swing',
				queue: false
			});
	}
	function RightDrawerSetXPosition( setXPos ) {
		RIGHT_DRAWER.animate(
			{
				marginRight: setXPos + 'px'
			},
			{
				duration: 35,
				easing: 'swing',
				queue: false
			});
	}

	/**
	 * Animates the element with id of param 'drawerID' to show or hide.
	 * @param	{string}	drawerID			ID field targeted for manipulation
	 * @param	{boolean}	setToOpenOrClosed	True: Drawer with id 'drawerID' is open/shown. False: Drawer is hidden.
	 */
	function DrawerOpenOrClose( drawerID, setToOpenOrClosed )
	{
		drawerID = drawerID.toLowerCase();

		// if ( setToOpenOrClosed === undefined )
		// {
		// console.log("Param 'setToOpenOrClosed was not defined'");
		// }
		// else if ( typeof setToOpenOrClosed != "boolean" )
		// {
		// console.log("Param 'setToOpenOrClosed' is not a boolean");
		// }
		// else // setToOpenOrClosed is defined as a boolean
		{
			if ( setToOpenOrClosed )	// Open
			{
				DRAWER_BACKDROP.fadeIn(200);
				if ( drawerID == 'mapdrawerleft' )	// There is probably a better way to do all this
				{
					LeftDrawerSetXPosition( LEFT_DRAWER_OPEN_POSITION );
				}
				else if ( drawerID == 'mapdrawerright' )
				{
					RightDrawerSetXPosition( LEFT_DRAWER_OPEN_POSITION );
				}
			}
			else // setToOpenOrClosed == false	// Close
			{
				DRAWER_BACKDROP.fadeOut(200);
				if ( drawerID == 'mapdrawerleft' )
				{
					LeftDrawerSetXPosition( LEFT_DRAWER_CLOSED_POSITION );
				}
				else if ( drawerID == 'mapdrawerright' )
				{
					RightDrawerSetXPosition( LEFT_DRAWER_CLOSED_POSITION );
				}
			}
		}
	}

	$(document).ready(function()
	{
		$("#MapLeftDrawerOpenButton").click(function()
		{
			DrawerOpenOrClose('MapDrawerLeft', true);
		});
		$("#MapLeftDrawerCloseButton").click(function()
		{
			DrawerOpenOrClose('MapDrawerLeft', false);
		});

		$("#MapDrawerRightOpenButton").click(function()
		{
			DrawerOpenOrClose('MapDrawerRight', true);
		});
		$(".rightDrawerCloseButton").click(function()
		{
			DrawerOpenOrClose('MapDrawerRight', false);
		});

		$("#MapDrawerBackdrop").click(function()
		{
			DrawerOpenOrClose('MapDrawerLeft', false);
			DrawerOpenOrClose('MapDrawerRight', false);
		});

		$("#MapDrawerBackdrop").fadeOut(300);
	});

	//============================================
	//==============================Swipe handling
	//============================================
	$(document).ready(function()
	{
		const DRAWERS = $(".MapDrawer"),
			SWIPE_DIRECTION_THRESHOLD = 10;
		let startX,
			startY,
			startTime,
			isVerticalSwipe = false,
			isHorizontalSwipe = false,
			hDisplacement;	// Horizontal displacement

		DRAWERS.on({
			touchstart: function(e)
			{
				let touchObject = e.changedTouches[0]	// Not 100% sure what this is. I guess it is an array of touch info.
				startX = touchObject.pageX;
				startY = touchObject.pageY;
				startTime = new Date().getTime();
			},
			touchmove: function(e)
			{
				if ( (isVerticalSwipe || isHorizontalSwipe) == true )
				{
					// Nothing happens when at least one is true.
					// Is this a bad practice? I find it easier to read the if statement this way.
				}
				else
				{
					let touchObject = e.changedTouches[0];
					if ( Math.abs(touchObject.pageY - startY) > SWIPE_DIRECTION_THRESHOLD )
					{
						isVerticalSwipe = true;
						console.log("Swipe determined to be vertical.");
					}
					if ( Math.abs(touchObject.pageX - startX) > SWIPE_DIRECTION_THRESHOLD )
					{
						isHorizontalSwipe = true;
						console.log("Swipe determined to be horizontal.");
					}
				}

				if ( isHorizontalSwipe )
				{
					e.preventDefault();	// Prevents the vertical scrolling that normally happens

					let touchObject = e.changedTouches[0];
					hDisplacement = touchObject.pageX - startX;

					if ( $(this).attr('id') == "MapDrawerLeft" )
					{
						hDisplacement = Math.min( 0, hDisplacement );

						$("#MapDrawerLeft").animate(
							{
								marginLeft: hDisplacement + 'px'
							},
							{
								duration: 10,
								queue: false
							}
						);
					}
					else if ( $(this).attr('id') == "MapDrawerRight" )
					{
						hDisplacement = Math.max( 0, hDisplacement );

						$("#MapDrawerRight").animate({
								marginRight: -hDisplacement + 'px'
							},
							{
								duration: 20,
								queue: false
							});
					}
				}

			},
			touchend: function(e)
			{
				if ( $(this).attr('id') == "MapDrawerLeft" )	// Yeah, this ain't scalable. At least there's only two drawers.
				{
					if ( isHorizontalSwipe == true && Math.abs(hDisplacement) > $("#MapDrawerLeft").width()/2 )
					{
						DrawerOpenOrClose('MapDrawerLeft', false);
					}
					else if ( isHorizontalSwipe == true )
					{
						// If the user does a fast enough swipe, the drawer will still be closed
						//	even if it doesn't reach half way.
						let elaspedTime = new Date().getTime() - startTime;
						let velocity = hDisplacement / elaspedTime	// px / ms
						console.log("elaspedTime: " + elaspedTime + "   Vel:" + velocity);

						if ( velocity <= -0.65 )
						{
							DrawerOpenOrClose('MapDrawerLeft', false);
						}
						else	// Not a fast swipe, nor is it half way. Reopen the drawer to full.
						{
							DrawerOpenOrClose('MapDrawerLeft', true);
						}
					}
				}
				else if ( $(this).attr('id') == "MapDrawerRight" )
				{
					if ( isHorizontalSwipe == true && Math.abs(hDisplacement) > $("#MapDrawerRight").width()/2 )
					{
						DrawerOpenOrClose('MapDrawerRight', false);
					}
					else if ( isHorizontalSwipe == true )
					{
						let elaspedTime = new Date().getTime() - startTime;
						let velocity = hDisplacement / elaspedTime	// px / ms
						console.log("elaspedTime: " + elaspedTime + "   Vel:" + velocity);

						if ( velocity >= 0.65 )
						{
							DrawerOpenOrClose('MapDrawerRight', false);
						}
						else
						{
							DrawerOpenOrClose('MapDrawerRight', true);
						}
					}
				}

				isVerticalSwipe = false;
				isHorizontalSwipe = false;
			}	// touchend end
		})
	});

})();
